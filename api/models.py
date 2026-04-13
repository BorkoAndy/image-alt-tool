import os
from http.server import BaseHTTPRequestHandler
import json
import google.generativeai as genai


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            models = [m.name for m in genai.list_models()]

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"models": models}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())