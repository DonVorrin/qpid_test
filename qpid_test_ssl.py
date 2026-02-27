from __future__ import print_function
import ssl 
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

class SendHandler(MessagingHandler):
    def __init__(self, url, address, message_body):
        super(SendHandler, self).__init__()
        self.url = url
        self.address = address
        self.message_body = message_body
        self.sent = False

    def on_start(self, event):
       
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE 

        conn = event.container.connect(self.url, ssl_domain=ssl_context)
        if conn:
            event.container.create_sender(conn, self.address)

    def on_sendable(self, event):
        if not self.sent:
            msg = Message(body=self.message_body)
            event.sender.send(msg)
            print("Message sent!")
            self.sent = True
            event.sender.close()
            event.connection.close()

    def on_accepted(self, event):
        print("Message accepted by server - access OK!")

    def on_disconnected(self, event):
        print("Disconnected")

    def on_rejected(self, event):
        print("Message rejected:", event.delivery.remote.condition)

try:
    url = "amqps://"
    address = "testQueue"
    message_body = "test"
    Container(SendHandler(url, address, message_body)).run()
    print("Sent successfully!")
except Exception as e:
    print("Failed:", e)
