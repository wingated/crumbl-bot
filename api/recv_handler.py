import os
from twilio.rest import Client
import openai

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

#
# ==========================================================================
#

class handler(BaseHTTPRequestHandler):

    def final_response( self, response ):
        self.send_response( 200 )
        self.send_header( 'Content-type', 'text/plain' )
        self.send_header( "Content-Length", str(len(response)) )
        self.end_headers()
        self.wfile.write( response )

    def do_GET(self):
        self.final_response( "Method not supported".encode() )
        return

    def parse_post( self ):
        content_length = int( self.headers['Content-Length'] )
        post_data = self.rfile.read( content_length )

        if type(post_data) == bytes:
            post_data = post_data.decode('utf-8')

        form = dict( parse_qs(post_data) )

        return form

    def do_POST(self):

        if not ( self.rfile and self.headers['Content-Length'] ):
            self.final_response( "(no data posted)".encode() )
            return

        form = self.parse_post()
        msg = form['Body'][0]
        user = form['From'][0]

        response = convo_turn( user, msg )

        response = response.encode()

        print( "HEY", response )

        self.final_response( response )
        return

#
# ==========================================================================
#

def convo_turn( user, msg ):
    # look up user, get conversation history
    # tack on latest convo turn
    # ping openai to get response
    # return response

    response = f"Hey {user}, thanks for saying '{msg}'"

    return response

#
# ==========================================================================
#

if __name__ == "__main__":
    try:
        HTTPServer(("0.0.0.0", 9000), handler).serve_forever()
    except KeyboardInterrupt:
        print('shutting down server')
