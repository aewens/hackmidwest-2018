from app import app, db, models
from flask import render_template
from twilio.rest import Client
from flask import request, redirect, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from re import match, findall
import requests

# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'ACe47bb3d689fcd1d09972b615e8efa9ba'
auth_token = '341b11b5f7a97a727b8c71c2fcc09467'
client = Client(account_sid, auth_token)

@app.route("/")
@app.route("/home")
def home():
    users = models.User.query.all()
    information = models.Info.query.all()
    kwargs = {
        "active": "home",
        "users": users,
        "information": information
    }
    return render_template("home.html", **kwargs)

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

@app.route("/edit/<user_id>", methods=["GET", "POST"])
def edit(user_id):
    if request.method == "POST":
        user_id = request.form.get("user_id")
        user = models.User.query.filter_by(id=user_id).one_or_none()
        name = request.form.get("name")
        gather_info = dict()
        attrs = list(request.form.keys())
        for attr in attrs:
            props = attr.split(":") if ":" in attr else None
            if props is None:
                continue

            if props[0] == "key":
                key = request.form.get(attr)
                index = props[1]
                gather_info[key] = request.form.get("value:%s" % index)

        all_info = models.Info.query.all()

        for info in all_info:
            if info.user[0].id == int(user_id):
                print(info)
                db.session.delete(info)
                
        information = []
        for key, value in gather_info.items():
            user_info = models.Info(key=key, value=str(value))
            db.session.add(user_info)
            information.append(user_info)
        
        user.info = information

        db.session.commit()
        return redirect(url_for("home"))
    else:
        user = models.User.query.filter_by(id=user_id).one_or_none()
        information = []
        for info in user.info:
            type_ = "Text"
            if match(r"^0\.", info.value):
                type_ = "Percent"
            elif match(r"^\d+$", info.value):
                type_ = "Number"

            information.append({
                "key": info.key,
                "value": info.value,
                "type": type_
            })
        kwargs = {
            "active": "edit",
            "user": user,
            "information": information,
            "user_id": user_id
        }
        return render_template("edit.html", **kwargs)

@app.route("/tweak", methods=["GET", "POST"])
def tweak():
    if request.method == "POST":
        return "Test"
    else:
        kwargs = {
            "active": "tweak"
        }
        return render_template("edit.html", **kwargs)

@app.route("/delete", methods=["POST"])
def delete():
    if request.method == "POST":
        user_id = request.json.get("user")
        user = models.User.query.filter_by(id=user_id).one_or_none()
        
        if user is None:
            return None

        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "success": True
        })

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

def check(word):
    return "," in word or "." in word or " and " in word

def split(word):
    if "," in word:
        words = word.split(",")
        for i, w in enumerate(words):
            print(2, "[%s]" % w, "<%s>" % words[i])
            if " and " in w:
                before = words[:i]
                current = words[i].split(" and ")[1]
                print(3, before, current)
                words = before + [current]
        words = [x.strip() for x in words]
        print(4, words)
        return words
    elif "." in word:
        return word.split(".")
    elif " and " in word:
        return word.split(" and ")

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
    pattern = r"(?:\sand\s)?([^\., ]+)"
    if word == 'order pizza' and participants.get(agent, 0) == 0:
        message = 'What choices?'
        participants[agent] = 1
    elif check(word) and participants.get(agent, 0) == 1:
        message = 'For how many?'
        choices = findall(pattern, word)
        participants[agent] = 2
    elif len(word) > 0 and participants.get(agent, 0) == 2:
        message = "Order ID: " + orderID
        counter = word
        participants[agent] = 3
        original = agent
    elif word == "3589" and participants.get(agent, 3) == 3:
        message = 'List preferences in order: %s' % ", ".join(choices)
        participants[agent] = 4
    elif len(split(word)) == len(choices) and participants.get(agent, 3) == 4:
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