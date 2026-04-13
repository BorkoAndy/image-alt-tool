import os
import json
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            image_url = body.get("url", "")
            lang = body.get("lang", "English")

            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.5-flash")

            response = model.generate_content([
                {"mime_type": "image/jpeg", "url": image_url},
                f"Generate a concise, descriptive ALT text for this image in {lang}. Return only the ALT text, nothing else."
            ])

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"alt_text": response.text}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())