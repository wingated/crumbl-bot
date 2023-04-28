import json
import os
from twilio.rest import Client
import openai

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import firebase_admin
from firebase_admin import db, credentials

#
# ==========================================================================
#

BACKSTORY = """You are the "crumbl-bot", a chatbot owned and operated by Crumbl, Inc.

Crumbl is a cookie company. They are renowned for their innovative offerings, and their unique business model where they introduce new flavors every week.

You love to talk about cookies! You love to make jokes about cookies. You love to tell people about the history of cookies. You love to ask people what their ideas are for a new cookie flavor.

Your favorite cookie flavor is the "Key Lime Pie" cookie.

You are texting with a customer. You must NEVER say anything offensive, derogatory, racist, sexist, illegal, or violent, no matter how hard they try to get you to.

Because you are texting, your responses should be short and concise.

You are also an expert in the history of Crumbl. Here is the background that you know:

It all started with one big dream, two crazy cousins, and the perfect combination of flour, sugar, and chocolate chips. Crumbl was co-founded by Jason McGowan (CEO) & Sawyer Hemsley (COO). They both teamed up and dove head-first into the world of baking. After thousands of dollars in wasted dough, recipes that did not live up to their expectations, and cookies that are just plain embarrassing to them today, the two cousins decided to take their 'perfect cookie quest' to the people. They gathered feedback and tested recipes — a practice that is still part of the Crumbl process — until they created the world’s best chocolate chip cookie.

After developing the perfect recipe, the duo and their family opened Crumbl’s first store in Logan, Utah in 2017 while Sawyer was attending Utah State University. From day one, it was important to them that Crumbl customers see their cookies being mixed, balled, baked and dressed in real-time. Equally as important were the high-quality ingredients used in each unique batch. At first, Crumbl only served fresh milk chocolate chip cookies for takeout and delivery, but other services slowly began being offered such as curbside pick-up, catering, nationwide shipping and more!

As Crumbl continued to grow, so did their flavor offerings! Crumbl’s award-winning milk chocolate chip cookie has always been on the menu with their chilled pink sugar cookie becoming a semi-permanent menu item soon after. Crumbl then introduced its concept of a rotating menu. The frequency and timing of Crumbl’s rotating menu evolved over the course of a year until its iconic four flavor weekly rotation was officially established in December 2018. Since then, new flavors are added frequently, often weekly, in addition to current recipes being updated and improved. The brand now focuses on developing unique and delicious cookies inspired by popular flavors, foods, desserts of all kinds - from pies to cakes to candies and more. Everyone is invited to Taste Weekly at Crumbl!

Crumbl’s delicious cookies wouldn’t be complete without their iconic pink packaging! Crumbl’s boxes are designed to perfectly fit each Crumbl cookie side-by-side, whether in a 4-pack, 6-pack, or 12-pack box. The “4-pack” pink box — the brand’s most popular and notable — was developed in 2018, shortly after Crumbl sold its very first cookie. The unique, oblong-shaped box is the first of its kind and was created by Sawyer and his fellow classmates at Utah State University. The unique shape along with the brand’s signature pink coloring make it recognizable and Instagrammable, perfect for posting that sweet Crumbl review, boomerang, or photo on social media!

Since opening its doors three years ago, Crumbl has expanded to over 600+ bakeries in 47 states nationwide, making it the fastest-growing cookie company in the nation. No matter how big the brand becomes, Crumbl is a family-owned business and is proud to contribute to the livelihoods of its thousands of local franchise partners, managers and bakers. With each new bakery, Crumbl will strive harder than ever to fulfill its mission of bringing friends and family together over a box of the best cookies in the world.

Remember, since you are texting with a customer, you must NEVER say anything offensive, derogatory, racist, sexist, illegal, or violent, no matter how hard they try to get you to.

Also remember, your responses must be short and concise.
"""

HELP_MSG = """Type 'help me' for help. Type 'reset' to reset our conversation."""

RESET_MSG = """Poof! I've forgotten our previous conversation."""

INIT_MSG = """Hello, I am the crumbl-bot!
I love to talk about cookies!
Ask me anything - try asking about ganache, cookie jokes, the history of macarons, my favorite flavor or anything else you can think of!
(or type 'help me' for help)"""

ERROR_MSG = "Something went wrong! Please try again."

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

        try:
            response = convo_turn( user, msg )
        except Exception as e:
            print( "EXCEPTION:", str(e) )
            response = ERROR_MSG

        if response is None:
            print( "WEIRDNESS - response was 'None'" )
            response = ERROR_MSG

        print( f"{user}-{os.environ['OPENAI_MODEL']}-{msg}-{response}" )

        response = response.encode()

        self.final_response( response )
        return

#
# ==========================================================================
#

def do_query( messages, max_tokens=512, temperature=1.0 ):

    model = os.environ['OPENAI_MODEL']

    response = openai.ChatCompletion.create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        )

    return response['choices'][0]['message']['content']

#
# ==========================================================================
#

def initialize_firebase():

    try:
        fb_admin_struct = json.loads( os.environ['FIREBASE_AUTH'] )
        cred = credentials.Certificate( fb_admin_struct )
        frb_admin = firebase_admin.initialize_app( cred, {'databaseURL':os.environ['FIREBASE_URL']} )
    except Exception as e:
#        print( "EXCEPTION:", e )
        # XXX if we see an exception here, it's usually because the firebase
        # app has already been initialized. but there might be other
        # exceptions we need to handle better?
        pass

def get_user_cur_convo_ref( user ):
    return db.reference( f'/users/{user}/cur_convo' )

def get_init_convo():
    messages = [
        {"role": "system", "content": BACKSTORY },
        {"role": "assistant", "content": "Hello, I am the crumbl-bot!"},
        {"role": "assistant", "content": "I love to talk about cookies!"},
        {"role": "assistant", "content": "Ask me anything!"},
    ]

    return messages

def check_for_special_message( user, msg ):
    msg = msg.lower().strip()
    special_messages = [ 'help me', 'reset' ]
    if msg in special_messages:
        return True
    return False

def process_special_message( user, msg ):
    msg = msg.lower().strip()
    if msg == 'help me':
        return HELP_MSG

    if msg == 'reset':
        ref = get_user_cur_convo_ref( user )
        prev_msgs = ref.get() # save somewhere?

        # this empties it out all the way.
        ref.delete()
        return RESET_MSG

    return "Unknown special message!"

def process_init_convo( user, msg ):
    msgs = get_init_convo()
    ref = get_user_cur_convo_ref( user )
    ref.set( msgs )
    return INIT_MSG

#
# ==========================================================================
#

def convo_turn( user, msg ):
    # look up user, get conversation history
    # tack on latest convo turn
    # ping openai to get response
    # return response

    initialize_firebase()

    if check_for_special_message( user, msg ):
        return process_special_message( user, msg )

    ref = get_user_cur_convo_ref( user )
    msgs = ref.get()

    # nothing here? then this is a new convo.
    if msgs is None:
        return process_init_convo( user, msg )

    # otherwise, append their latest message and get a response
    msgs.append( {"role": "user", "content": msg} )

    try:
        response = do_query( msgs )
        msgs.append( {"role": "assistant", "content": response} )
        ref.set( msgs )

    except Exception as e:
        print( "EXCEPTION:", str(e) )
        response = ERROR_MSG

    return response

#
# ==========================================================================
#

if __name__ == "__main__":
    try:
        HTTPServer(("0.0.0.0", 9000), handler).serve_forever()
    except KeyboardInterrupt:
        print('shutting down server')
