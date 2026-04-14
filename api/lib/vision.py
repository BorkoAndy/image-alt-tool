import os
import urllib.request
import base64
import google.generativeai as genai
from groq import Groq

# Max image size: 10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024 
ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']

def analyze_image(image_url=None, base64_data=None, model="gemini", lang="English"):
    """
    Analyzes an image and generates ALT text.
    Supports either a public URL or base64 encoded data.
    """
    image_bytes = None
    content_type = None

    if base64_data:
        # Handle base64 data
        if ',' in base64_data:
            header, base64_data = base64_data.split(',', 1)
            if 'image/' in header:
                content_type = header.split(';')[0].split(':')[1]
        
        image_bytes = base64.b64decode(base64_data)
        if not content_type:
            # Fallback to jpeg if not specified, or try to detect
            content_type = "image/jpeg" 
    elif image_url:
        # 1. Verify and Download Image
        verify_image(image_url)
        with urllib.request.urlopen(image_url, timeout=10) as resp:
            image_bytes = resp.read()
            content_type = resp.headers.get_content_type()
    else:
        raise ValueError("Either image_url or base64_data must be provided.")

    # Final size check for both sources
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(f"Image is too large ({len(image_bytes) // 1024 // 1024}MB). Max size is 10MB.")

    prompt = f"Generate a concise, descriptive ALT text for this image in {lang}. Maximum 100 characters. Return only the ALT text, nothing else. If the image is NSFW, harmful, or violates safety guidelines, return ONLY the word 'UNSAFE'."

    if model == "groq":
        alt_text, limits = _analyze_with_groq(image_bytes, content_type, prompt)
    else:
        alt_text, limits = _analyze_with_gemini(image_bytes, content_type, prompt)

    # 2. Hard Block Unsafe Content
    if alt_text.strip().upper() == "UNSAFE":
        raise ValueError("Image content violates safety guidelines.")

    return alt_text, limits

def verify_image(image_url):
    """
    Performs basic validation of the image before processing.
    """
    try:
        req = urllib.request.Request(image_url, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as resp:
            content_type = resp.headers.get_content_type()
            content_length = resp.headers.get('Content-Length')

            if content_type not in ALLOWED_CONTENT_TYPES:
                raise ValueError(f"Unsupported image format: {content_type}. Please use JPEG, PNG, WEBP, or GIF.")

            if content_length and int(content_length) > MAX_IMAGE_SIZE:
                raise ValueError(f"Image is too large ({int(content_length) // 1024 // 1024}MB). Max size is 10MB.")
    except Exception as e:
        if isinstance(e, ValueError): raise e
        # If HEAD fails, we'll try to let the AI handle it or catch it during full download
        pass

def _analyze_with_groq(image_bytes, content_type, prompt):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Convert bytes to base64 data URI for Groq
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    image_url = f"data:{content_type};base64,{base64_image}"

    completion = client.chat.completions.with_raw_response.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    headers = completion.headers
    result = completion.parse()
    alt_text = result.choices[0].message.content

    limits = {
        "rpm_remaining": headers.get("x-ratelimit-remaining-requests", "?"),
        "rpm_limit": headers.get("x-ratelimit-limit-requests", "?"),
        "rpd_remaining": headers.get("x-ratelimit-remaining-requests-day", "?"),
        "rpd_limit": headers.get("x-ratelimit-limit-requests-day", "?"),
    }
    
    return alt_text, limits

def _analyze_with_gemini(image_bytes, content_type, prompt):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Configure safety settings to block unsafe content
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    gemini = genai.GenerativeModel("gemini-1.5-flash", safety_settings=safety_settings)
    
    try:
        response = gemini.generate_content([
            prompt,
            {"mime_type": content_type, "data": image_bytes}
        ])
        return response.text, None
    except Exception as e:
        # Check if it was blocked by safety
        if "safety" in str(e).lower() or "block" in str(e).lower():
            raise ValueError("Image content violates safety guidelines.")
        raise e
