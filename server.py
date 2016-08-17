from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import zulip
import sys
import threading
import json
import requests

# Please fill in all constants before operating
# Also ensure groupme has the correct callback URI on their end. 
ZULIP_STREAM      = "my_stream"
ZULIP_TOPIC       = "Bot_testing"
ZULIP_BOT_EMAIL   = "notarealemail-bot@andrew.cmu.edu"
ZULIP_API_KEY     = "not-my-api-key"
ZULIP_URL         = "https://andrew.zulipchat.com/api"
GROUPME_BOT_ID    = "not-my-bot-id"
GROUPME_PORT      = 8000

# These two are very important, they stop the bot from echoing itself
ZULIP_BOT_NAME    = "Groupme_bot"
GROUPME_BOT_NAME  = "ABTech Bot"

# Make a post request to the groupme api to post to a chat.
def send_to_groupme(msg):
    if(msg['sender_full_name'] != ZULIP_BOT_NAME):
        requests.post("https://api.groupme.com/v3/bots/post", 
          data={'bot_id': GROUPME_BOT_ID, 
                'text': msg['sender_full_name'] + ": " + msg['content']})

# Use the python zulip functions to post to a stream
def send_to_zulip(msg):
    if(msg['name'] != GROUPME_BOT_NAME):
        client.send_message({
            "type": "stream",
            "to": ZULIP_STREAM,
            "subject": ZULIP_TOPIC,
            "content": msg['name'] + ": " + msg['text']
        })

# Handler for the groupme messages
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        send_to_zulip(post_data)
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")

# Actual server to handle the groupme messages  
def run_groupme_listener():
    server_address = ('', GROUPME_PORT)
    httpd = HTTPServer(server_address, S)
    print 'Starting httpd...'
    httpd.serve_forever()

# Wrapper for the zulip listener for threading
def run_zulip_listener():
    client.call_on_each_message(send_to_groupme)

# Start zulip listener in the background
client = zulip.Client(email=ZULIP_BOT_EMAIL, api_key=ZULIP_API_KEY, site=ZULIP_URL)
t = threading.Thread(target=run_zulip_listener)
t.setDaemon(True)
t.start()

#start the groupme listener as the main service
run_groupme_listener()
