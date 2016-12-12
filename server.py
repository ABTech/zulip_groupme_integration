from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import zulip
import sys
import threading
import json
import requests
import secrets

# !!! Please fill in all constants in secrets.py before operating !!!

# Make a post request to the groupme api to post to a chat.
def send_to_groupme(msg):
    if(msg['sender_full_name'] != secrets.ZULIP_BOT_NAME and msg['subject'] == secrets.ZULIP_TOPIC):
        requests.post("https://api.groupme.com/v3/bots/post", 
          data={'bot_id': secrets.GROUPME_BOT_ID, 
                'text': msg['sender_full_name'] + ": " + msg['content']})

# Use the python zulip functions to post to a stream
def send_to_zulip(msg):
    if(msg['name'] != secrets.GROUPME_BOT_NAME):
        client.send_message({
            "type": "stream",
            "to": secrets.ZULIP_STREAM,
            "subject": secrets.ZULIP_TOPIC,
            "content": "**" + msg['name'] + "**: " + msg['text']
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

# Actual server to handle the groupme messages  
def run_groupme_listener():
    server_address = ('', secrets.GROUPME_PORT)
    httpd = HTTPServer(server_address, S)
    print 'Starting httpd...'
    httpd.serve_forever()

# Wrapper for the zulip listener for threading
def run_zulip_listener():
    client.call_on_each_message(send_to_groupme)

# Start zulip listener in the background
client = zulip.Client(email=secrets.ZULIP_BOT_EMAIL, api_key=secrets.ZULIP_API_KEY, site=secrets.ZULIP_URL)
t = threading.Thread(target=run_zulip_listener)
t.setDaemon(True)
t.start()

#start the groupme listener as the main service
run_groupme_listener()
