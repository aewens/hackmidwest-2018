#!env/bin/python3

# # Download the helper library from https://www.twilio.com/docs/python/install
# from twilio.rest import Client


# # Your Account Sid and Auth Token from twilio.com/console
# account_sid = 'ACe47bb3d689fcd1d09972b615e8efa9ba'
# auth_token = '341b11b5f7a97a727b8c71c2fcc09467'
# client = Client(account_sid, auth_token)

# message = client.messages.create(
#                               body='Hello there!',
#                               from_='+18162088161',
#                               to='+18165163095'
#                           )

# print(message.sid)

################################################################################################

# from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse

# response = MessagingResponse()
# message = Message()
# message.body('Hello World!')
# response.append(message)
# response.redirect('https://demo.twilio.com/welcome/sms/')

# print(response)

################################################################################################

# import os
# from flask import Flask, request, redirect
# from twilio.twiml.messaging_response import MessagingResponse

# app = Flask(__name__)

# @app.route("/sms", methods=['GET', 'POST'])
# def sms_reply():
#     resp = MessagingResponse()

#     resp.message("Test Message")

#     return str(resp)

#     i = 0

# if __name__ == "__main__":
#     app.run(debug=True)

################################################################################################

# from flask import Flask, request, session
# from twilio.twiml.messaging_response import MessagingResponse

# # The session object makes use of a secret key.
# SECRET_KEY = 'a secret key'
# app = Flask(__name__)
# app.config.from_object(__name__)

# # Try adding your own number to this list!
# callers = {
#     "+18165182950": "Austin",
#     "+18165163095": "Garrett",
# }


# @app.route("/sms", methods=['GET', 'POST'])
# def hello():
#     """Respond with the number of text messages sent between two parties."""
#     # Increment the counter
#     counter = session.get('counter', 0)
#     counter += 1

#     # Save the new counter value in the session
#     session['counter'] = counter

#     from_number = request.values.get('From')
#     if from_number in callers:
#         name = callers[from_number]
#     else:
#         name = "Friend"

#     # Build our reply
#     message = '{} has messaged {} {} times.' \
#         .format(name, request.values.get('To'), counter)

#     # Put it in a TwiML response
#     resp = MessagingResponse()
#     resp.message(message)

#     return str(resp)


# if __name__ == "__main__":
#     app.run(debug=True)

################################################################################################

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