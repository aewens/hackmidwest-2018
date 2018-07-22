from app import app, db, models
from flask import render_template
from twilio.rest import Client
from flask import request, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse
import requests

# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'ACe47bb3d689fcd1d09972b615e8efa9ba'
auth_token = '341b11b5f7a97a727b8c71c2fcc09467'
client = Client(account_sid, auth_token)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", active="home")

@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        name = request.form.get("name")
        info = dict()
        attrs = list(request.form.keys())
        for attr in attrs:
            props = attr.split(":") if ":" in attr else None
            if props is None:
                continue

            if props[0] == "key":
                key = request.form.get(attr)
                index = props[1]
                info[key] = request.form.get("value:%s" % index)

        user = models.User(name=name)
        for key, value in info.items():
            user_info = models.Info(key=key, value=str(value))
            db.session.add(user_info)
            user.info.append(user_info)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("new"))
    else:
        return render_template("new.html", active="new")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        return "Test"
    else:
        return render_template("edit.html", active="edit")

orderID = "3589"
decisions = []
counter = 0
choices = ""
participants = {}
original = ""

def notifyOriginal(original):
    requests.post("https://removeo.serveo.net/sms/override", {
        "body": "debug",
        "from_": "+18162088161",
        "to": original
    })

@app.route("/sms", methods=['GET', 'POST'])
@app.route("/sms/<command>", methods=['GET', 'POST'])
def reply(command=None):
    global orderId
    global decisions
    global counter
    global choices
    global participants
    global original

    if command == "override":
        body = request.values.get("body")
        from_ = request.values.get("from_")
        to = request.values.get("to")
        message = client.messages.create(body=body, from_=from_,to=to)
        resp = MessagingResponse()
        resp.message(message)

        return str(resp)

    sms_sid = request.values.get("SmsSid")
    sms_message = client.messages(sms_sid).fetch()
    word = sms_message.body.strip().lower()
    agent = sms_message.from_
    if word == 'order pizza' and participants.get(agent, 0) == 0:
        message = 'What choices?'
        participants[agent] = 1
    elif len(word.split(",")) == 3 and participants.get(agent, 0) == 1:
        message = 'For how many?'
        choices = word
        participants[agent] = 2
    elif len(word) > 0 and participants.get(agent, 0) == 2:
        message = "Order ID: " + orderID
        counter = word
        participants[agent] = 3
        original = agent
    elif word == "3589" and participants.get(agent, 3) == 3:
        message = 'List preferences in order: %s' % choices
        participants[agent] = 4
    elif len(word.split(",")) == 3 and participants.get(agent, 3) == 4:
        decisions.append(word)
        message = 'Thank you!'
        participants[agent] = 0
        counter = int(counter) - 1
        if counter == 0:
            notifyOriginal(original)
    else:
        message = 'Invalid'
    resp = MessagingResponse()
    resp.message(message)
    

    return str(resp)