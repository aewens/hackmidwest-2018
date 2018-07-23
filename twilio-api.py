#!env/bin/python3

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)

# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'ACe47bb3d689fcd1d09972b615e8efa9ba'
auth_token = '341b11b5f7a97a727b8c71c2fcc09467'
client = Client(account_sid, auth_token)

messages = client.messages.list()

def reverse(message):
    return message[::-1]

@app.route("/sms", methods=['GET', 'POST'])
def reply():
    sms_sid = request.values.get("SmsSid")
    word = client.messages(sms_sid).fetch().body.strip().lower()
    if word == 'ready':
        message = 'Go'
    else:
        message = "You did not say 'ready'"

    resp = MessagingResponse()
    resp.message(reverse(message))

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)