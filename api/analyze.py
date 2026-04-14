import os
import json
from http.server import BaseHTTPRequestHandler
import urllib.request
import google.generativeai as genai
from groq import Groq


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            image_url = body.get("url", "")
            model = body.get("model", "gemini")
            lang = body.get("lang", "English")

            prompt = f"Generate a concise, descriptive ALT text for this image in {lang}. Maximum 100 characters. Return only the ALT text, nothing else."

            if model == "groq":
                client = Groq(api_key=os.environ["GROQ_API_KEY"])
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

            else:
                genai.configure(api_key=os.environ["GEMINI_API_KEY"])
                gemini = genai.GenerativeModel("gemini-2.5-flash")
                with urllib.request.urlopen(image_url) as resp:
                    image_data = resp.read()
                    content_type = resp.headers.get_content_type()
                response = gemini.generate_content([
                    prompt,
                    {"mime_type": content_type, "data": image_data}
                ])
                alt_text = response.text
                limits = None

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "alt_text": alt_text,
                "limits": limits
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())