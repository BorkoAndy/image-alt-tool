import json
from http.server import BaseHTTPRequestHandler
import sys
import os

# Add the current directory to path so we can import from lib
sys.path.append(os.path.dirname(__file__))
from lib.vision import analyze_image

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            
            image_url = body.get("url", "")
            image_data = body.get("image_data", "")
            model = body.get("model", "gemini")
            lang = body.get("lang", "English")

            if not image_url and not image_data:
                raise ValueError("Image URL or Image Data is required")

            # Call the extracted vision logic
            alt_text, limits = analyze_image(image_url=image_url, base64_data=image_data, model=model, lang=lang)

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