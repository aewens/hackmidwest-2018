from app import app, db, models
from flask import render_template
from twilio.rest import Client
from flask import request, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse

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