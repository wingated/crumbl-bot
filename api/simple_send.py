import os
from twilio.rest import Client

from http.server import BaseHTTPRequestHandler
from datetime import datetime

class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token  = os.environ['TWILIO_AUTH_TOKEN']
        number_from = os.environ['TWILIO_FROM_NUMBER']
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            to="+15088080619",
            from_=number_from,
            body="Simple send!")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        response = message.sid

        self.wfile.write( response.encode() )

        return
