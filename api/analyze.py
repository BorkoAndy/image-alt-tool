import os
import json
from http.server import BaseHTTPRequestHandler
import urllib.request
import google.generativeai as genai


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            image_url = body.get("url", "")
            lang = body.get("lang", "English")

            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.0-flash")

            with urllib.request.urlopen(image_url) as resp:
                image_data = resp.read()
                content_type = resp.headers.get_content_type()

            response = model.generate_content([
                f"Generate a concise, descriptive ALT text for this image in {lang}. Return only the ALT text, nothing else.",
                {"mime_type": content_type, "data": image_data}
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