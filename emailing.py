# import sys

# sys.path.insert(0, './config/')

import smtplib, secrets
from email import message

def send_email(body):
	msg = message.Message()
	msg.add_header("from", secrets.smtp_from_addr)
	msg.add_header("to", secrets.smtp_to_addr)
	msg.add_header("subject", "CCBTool Status")
	msg.set_payload(body)
	
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.ehlo()
	server.starttls()
	server.login(secrets.smtp_from_addr, secrets.smtp_password)

	print("sending status message")
	server.send_message(msg, from_addr=secrets.smtp_from_addr, to_addrs=secrets.smtp_to_addr.split(","))