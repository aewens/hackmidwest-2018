from app import app, db, models
from flask import render_template
from twilio.rest import Client
from flask import request, redirect, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from re import match
import requests
import math

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

def base(apply, mode, target, processing):
    rank = dict()
    for _, entry in processing.items():
        print("****")
        for attr, props in entry.items():
            size = len(props)
            if mode == "lin":
                for i, prop in enumerate(props):
                    rank[attr] = rank.get(attr, dict())
                    rank[attr][prop] = rank[attr].get(prop, 0)
                    rank[attr][prop] += apply(size, i)
                    print("*", prop, i, apply(size, i))
            elif mode == "exp":
                for i, prop in enumerate(props):
                    rank[attr] = rank.get(attr, dict())
                    rank[attr][prop] = rank[attr].get(prop, 0)
                    rank[attr][prop] += apply(size, i) * size**2
                    print("*", prop, i, apply(size, i) * size**2)
            elif mode == "log":
                for i, prop in enumerate(props):
                    rank[attr] = rank.get(attr, dict())
                    rank[attr][prop] = rank[attr].get(prop, 0)
                    rank[attr][prop] += math.log(apply(size, i))
                    print("*", prop, i, math.log(apply(size, i)))

    return rank

def maximize(mode, target, processing):
    apply = lambda size, index: index
    return base(apply, mode, target, processing)

def minimize(mode, target, processing):
    apply = lambda size, index: -index
    return base(apply, mode, target, processing)

def standard(mode, target, processing):
    apply = lambda size, index: math.floor(size/2) - index
    return base(apply, mode, target, processing)

@app.route("/think", methods=["GET", "POST"])
def think():
    if request.method == "POST":
        skip = request.json.get("skip", None)
        processing = dict()
        target = None
        if skip is not None:
            data = request.json.get("data", [])
            target = request.json.get("target", "data")
            for i, d in enumerate(data):
                payload = dict()
                payload[target] = d
                processing[i] = payload
        else:
            user_ids = request.json.get("users", "").split(",")
            user_ids = [int(user_id) for user_id in user_ids]
            info_keys = request.json.get("keys", "").split(",")
            target = request.json.get("target", None)
            users = models.User.query.all()
            information = models.Info.query.all()
            print(1, user_ids)
            print(2, info_keys)
            print(3, users)
            print(4, information)

            used_users = [u for u in users if u.id in user_ids]
            print(5, used_users)
            
            for user in used_users:
                used_info = [i for i in user.info if i.key in info_keys]
                if target is None and len(used_info) == 1:
                    target = used_info[0].key

                for uinfo in used_info:
                    uid = uinfo.user[0].id
                    processing[uid] = processing.get(uid, dict())
                    props = [prop.strip() for prop in uinfo.value.split(",")]
                    processing[uid][uinfo.key] = props

        goals = {
            "+": maximize, 
            "-": minimize,
            "0": standard
        }
        goal = goals.get(request.json.get("goal"), "-")
        modes = ["lin", "exp", "log"]
        mode = request.json.get("mode", "")
        mode = mode if mode in modes else "lin"
        print(6, goal, mode, target, processing)

        decision = goal(mode, target, processing)
        print(7, decision)
        # db.session.delete(user)
        # db.session.commit()
        return jsonify({
            "success": True
        })
    else:
        users = models.User.query.all()
        information = models.Info.query.all()

        user_info = dict()
        info_export = dict()
        for info in information:
            iuser = info.user[0]
            uid = iuser.id
            type_ = "Text"
            if match(r"^0\.", info.value):
                type_ = "Percent"
            elif match(r"^\d+$", info.value):
                type_ = "Number"
            info_dict = {
                "id": info.id,
                "key": info.key,
                "value": info.value,
                "type": type_
            }
            user_info[uid] = user_info.get(uid, [])
            user_info[uid].append(info_dict)
            info_dict["user"] = uid
            info_export[info.key] = info_export.get(info.key, [])
            info_export[info.key].append(uid)
            
        users_export = list()
        for user in users:
            users_export.append({
                "id": user.id,
                "name": user.name,
                "info": user_info[user.id]
            })

        kwargs = {
            "active": "think",
            "users": users_export,
            "information": info_export
        }
        return render_template("think.html", **kwargs)

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