import os
import urlparse
from twilio.rest import Client

from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write( "Method not supported".encode() )
        return

    def do_POST(self):

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        response = ""
        if self.rfile:
             # print urlparse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])))
             for key,value in dict(urlparse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])))).items():
                 response += key + " = " + value[0]

        self.wfile.write( response.encode() )

        return
