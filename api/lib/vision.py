import os
import json
import urllib.request
import base64
import google.generativeai as genai
from groq import Groq

# Max image size: 10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']


def analyze_image(image_url=None, base64_data=None, model="groq", lang="English"):
    """Single language mode — returns alt_text and limits."""
    image_bytes, content_type = _load_image(image_url, base64_data)

    prompt = (
        f"Generate a concise, descriptive ALT text for this image in {lang}. "
        f"Maximum 100 characters. Return only the ALT text, nothing else. "
        f"If the image is NSFW, harmful, or violates safety guidelines, return ONLY the word 'UNSAFE'."
    )

    if model == "groq":
        result, limits = _analyze_with_groq(image_bytes, content_type, prompt)
    else:
        result, limits = _analyze_with_gemini(image_bytes, content_type, prompt)

    if result.strip().upper() == "UNSAFE":
        raise ValueError("Image content violates safety guidelines.")

    return result, limits


def analyze_image_multi(image_url=None, base64_data=None, model="groq", languages=None):
    """
    Multi-language mode — one API call returns title, alt, caption for all languages.
    Language codes are passed directly to the AI (no hardcoded mapping needed).
    Returns meta dict and limits.
    """
    if not languages:
        languages = ["en"]

    image_bytes, content_type = _load_image(image_url, base64_data)

    example = {l: {"alt": "...", "title": "...", "caption": "..."} for l in languages}

    prompt = (
        f"Analyze this image and return a JSON object with metadata.\n\n"
        f"Use these exact language codes as keys: {languages}\n"
        f"For each language code, generate the text in the corresponding language "
        f"(e.g. 'de' = German, 'en' = English, 'ru' = Russian, 'nl' = Dutch, "
        f"'fr' = French, 'it' = Italian, 'es' = Spanish, 'pl' = Polish, "
        f"'zh' = Chinese, 'ja' = Japanese, 'ar' = Arabic, etc.)\n\n"
        f"Return exactly this structure:\n{json.dumps(example, indent=2)}\n\n"
        f"Rules:\n"
        f"- alt: max 100 characters, descriptive ALT text for accessibility\n"
        f"- title: max 60 characters, short image title\n"
        f"- caption: max 160 characters, descriptive subtitle\n"
        f"- Return ONLY valid JSON, no markdown, no explanation\n"
        f"- If image is NSFW or violates safety guidelines, return only the word UNSAFE"
    )

    if model == "groq":
        result_text, limits = _analyze_with_groq(image_bytes, content_type, prompt)
    else:
        result_text, limits = _analyze_with_gemini(image_bytes, content_type, prompt)

    if result_text.strip().upper() == "UNSAFE":
        raise ValueError("Image content violates safety guidelines.")

    clean = result_text.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    meta = json.loads(clean)
    return meta, limits


def verify_image(image_url):
    """Performs basic validation of the image before processing."""
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
        if isinstance(e, ValueError):
            raise e
        pass


def _load_image(image_url, base64_data):
    """Loads image from URL or base64 and returns (image_bytes, content_type)."""
    image_bytes = None
    content_type = None

    if base64_data:
        if ',' in base64_data:
            header, base64_data = base64_data.split(',', 1)
            if 'image/' in header:
                content_type = header.split(';')[0].split(':')[1]
        image_bytes = base64.b64decode(base64_data)
        if not content_type:
            content_type = "image/jpeg"

    elif image_url:
        verify_image(image_url)
        with urllib.request.urlopen(image_url, timeout=10) as resp:
            image_bytes = resp.read()
            content_type = resp.headers.get_content_type()
    else:
        raise ValueError("Either image_url or base64_data must be provided.")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(f"Image is too large ({len(image_bytes) // 1024 // 1024}MB). Max size is 10MB.")

    return image_bytes, content_type


def _analyze_with_groq(image_bytes, content_type, prompt):
    """Calls Groq vision API and returns (result_text, limits)."""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    image_data_url = f"data:{content_type};base64,{base64_image}"

    completion = client.chat.completions.with_raw_response.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url}
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
    text = result.choices[0].message.content

    limits = {
        "rpm_remaining": headers.get("x-ratelimit-remaining-requests", "?"),
        "rpm_limit": headers.get("x-ratelimit-limit-requests", "?"),
        "rpd_remaining": headers.get("x-ratelimit-remaining-requests-day", "?"),
        "rpd_limit": headers.get("x-ratelimit-limit-requests-day", "?"),
    }

    return text, limits


def _analyze_with_gemini(image_bytes, content_type, prompt):
    """Calls Gemini vision API and returns (result_text, limits)."""
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    gemini = genai.GenerativeModel("gemini-2.5-flash", safety_settings=safety_settings)

    try:
        response = gemini.generate_content([
            prompt,
            {"mime_type": content_type, "data": image_bytes}
        ])
        return response.text, None
    except Exception as e:
        if "safety" in str(e).lower() or "block" in str(e).lower():
            raise ValueError("Image content violates safety guidelines.")
        raise e
