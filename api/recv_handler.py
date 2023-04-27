import os
from twilio.rest import Client

from http.server import BaseHTTPRequestHandler, HTTPServer

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write( "Method not supported".encode() )
        return

    def do_POST(self):

        if self.rfile and self.headers['Content-Length']:
            content_length = int( self.headers['Content-Length'] )
            response = f"Got post data: {content_length}\n"
            post_data = self.rfile.read( content_length )
            response += post_data.decode('utf-8')
        else:
            response = "(no data posted)"
             # print urlparse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])))
#             for key,value in dict(urlparse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])))).items():
#                 response += key + " = " + value[0]

        response = response.encode()

        print( "HEY", response )

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write( response )

        print( "DONE" )

        return

if __name__ == "__main__":
    try:
        HTTPServer(("0.0.0.0", 9000), handler).serve_forever()
    except KeyboardInterrupt:
        print('shutting down server')
