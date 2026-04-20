import json
from http.server import BaseHTTPRequestHandler
import sys
import os

# Add the current directory to path so we can import from lib
sys.path.append(os.path.dirname(__file__))
from lib.vision import analyze_image, analyze_image_multi


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Simple Authentication Check
            auth_header = self.headers.get("Authorization")
            app_password = os.environ.get("APP_PASSWORD")

            if app_password and auth_header != app_password:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            image_url = body.get("url", "")
            image_data = body.get("image_data", "")
            model = body.get("model", "groq")
            languages = body.get("languages", [])  # e.g. ["de", "en", "ru"]
            lang = body.get("lang", "English")      # fallback single lang

            if not image_url and not image_data:
                raise ValueError("Image URL or Image Data is required")

            # Multi-language mode
            if languages:
                meta, limits = analyze_image_multi(
                    image_url=image_url,
                    base64_data=image_data,
                    model=model,
                    languages=languages
                )
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "meta": meta,
                    "limits": limits
                }).encode())

            # Single language mode (backwards compatible)
            else:
                alt_text, limits = analyze_image(
                    image_url=image_url,
                    base64_data=image_data,
                    model=model,
                    lang=lang
                )
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
