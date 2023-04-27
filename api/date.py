import os

from http.server import BaseHTTPRequestHandler
from datetime import datetime

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        response = f"SID: {os.environ['TWILIO_ACCOUNT_SID']}, AUTH: {os.environ['TWILIO_AUTH_TOKEN']}, PHONE: {os.environ['TWILIO_FROM_NUMBER']}"
        response += str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.wfile.write( response.encode() )
        return
