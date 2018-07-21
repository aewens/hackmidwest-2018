#!env/bin/python3

# # Download the helper library from https://www.twilio.com/docs/python/install
# from twilio.rest import Client


# # Your Account Sid and Auth Token from twilio.com/console
# account_sid = 'ACedafea7bfb9ef41f63661da58b77dd98'
# auth_token = '816c900a579d1dfc6bf3faa1025b9da8'
# client = Client(account_sid, auth_token)

# message = client.messages.create(
#                               body='Hello there!',
#                               from_='+18162538090',
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

from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)

# Try adding your own number to this list!
callers = {
    "+18165182950": "Austin",
    "+18165163095": "Garrett",
    #"+14158675311": "Chewy",
}


@app.route("/sms", methods=['GET', 'POST'])
def hello():
    """Respond with the number of text messages sent between two parties."""
    # Increment the counter
    counter = session.get('counter', 0)
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    from_number = request.values.get('From')
    if from_number in callers:
        name = callers[from_number]
    else:
        name = "Friend"

    # Build our reply
    message = '{} has messaged {} {} times.' \
        .format(name, request.values.get('To'), counter)

    # Put it in a TwiML response
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)