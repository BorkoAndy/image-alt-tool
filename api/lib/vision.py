import os
import urllib.request
import google.generativeai as genai
from groq import Groq

def analyze_image(image_url, model="gemini", lang="English"):
    """
    Analyzes an image and generates ALT text using Gemini or Groq.
    """
    prompt = f"Generate a concise, descriptive ALT text for this image in {lang}. Maximum 100 characters. Return only the ALT text, nothing else."

    if model == "groq":
        return _analyze_with_groq(image_url, prompt)
    else:
        return _analyze_with_gemini(image_url, prompt)

def _analyze_with_groq(image_url, prompt):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
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

def _analyze_with_gemini(image_url, prompt):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    gemini = genai.GenerativeModel("gemini-2.5-flash")
    
    with urllib.request.urlopen(image_url) as resp:
        image_data = resp.read()
        content_type = resp.headers.get_content_type()
    
    response = gemini.generate_content([
        prompt,
        {"mime_type": content_type, "data": image_data}
    ])
    
    return response.text, None
