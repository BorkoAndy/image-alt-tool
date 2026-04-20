import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(410)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        message = {
            "error": "DEPRECATED",
            "message": "This endpoint has been moved to /api/v1/analyze. Please update your client configuration.",
            "documentation": "https://image-alt-tool.vercel.app/api/v1/docs"
        }
        self.wfile.write(json.dumps(message).encode())

    def do_GET(self):
        self.do_POST()
