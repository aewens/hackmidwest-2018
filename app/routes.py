from app import app
from flask import render_template
from twilio.rest import Client
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse

# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'ACe47bb3d689fcd1d09972b615e8efa9ba'
auth_token = '341b11b5f7a97a727b8c71c2fcc09467'
client = Client(account_sid, auth_token)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/sms", methods=['GET', 'POST'])
def reply():
    sms_sid = request.values.get("SmsSid")
    word = client.messages(sms_sid).fetch().body.strip().lower()
    if word == 'ready':
        message = 'Go'
    else:
        message = "You did not say 'ready'"

    resp = MessagingResponse()
    resp.message(message)

    return str(resp)