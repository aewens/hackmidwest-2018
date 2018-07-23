from app import app, db, models
from flask import render_template
from twilio.rest import Client
from flask import request, redirect, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from re import match, findall
from random import randint
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
        modifier = 0
        for attr, modify in entry.items():
            if attr == target:
                continue

            modifier += float(modify[0])

        props = entry[target]
        size = len(props)
        if mode == "lin":
            for i, prop in enumerate(props):
                imod = modifier * (1 - i / size)
                rank[target] = rank.get(target, dict())
                rank[target][prop] = rank[target].get(prop, 0)
                rank[target][prop] += apply(size, i) + imod
                print("&", prop, i, apply(size, i), apply(size, i) + imod)
        elif mode == "exp":
            for i, prop in enumerate(props):
                imod = modifier * (1 - i / size)
                rank[target] = rank.get(target, dict())
                rank[target][prop] = rank[target].get(prop, 0)
                rank[target][prop] += apply(size, i) * size**2 + imod
                print("*", prop, i, apply(size, i) * size**2 + imod)
        elif mode == "log":
            for i, prop in enumerate(props):
                imod = modifier * (1 - i / size)
                rank[target] = rank.get(target, dict())
                rank[target][prop] = rank[target].get(prop, 0)
                rank[target][prop] += math.log(apply(size, i)) + imod
                print("*", prop, i, math.log(apply(size, i)) + imod)
                
    print("%", rank)
    decision = None
    highest = None
    tied = True
    options = list()
    for prop, rnk in rank[target].items():
        options.append(prop)
        if highest is None:
            decision = prop
            highest = rnk
        elif rnk > highest or rnk < highest:
            tied = False

        if rnk > highest:
            decision = prop
            highest = rnk

    if tied:
        decision = options[randint(0, len(options) - 1)]

    return decision

def positive(mode, target, processing):
    apply = lambda size, index: size - index
    return base(apply, mode, target, processing)

def negative(mode, target, processing):
    apply = lambda size, index: -index
    return base(apply, mode, target, processing)

def standard(mode, target, processing):
    apply = lambda size, index: math.floor(size/2) - index
    return base(apply, mode, target, processing)

@app.route("/think", methods=["GET", "POST"])
def think():
    if request.method == "POST":
        skip = request.values.get("skip", None)
        processing = dict()
        target = None
        goals = {
            "+": positive, 
            "-": negative,
            "0": standard
        }
        modes = ["lin", "exp", "log"]
        if skip is not None:
            data = request.values.get("data", "").split("|")
            target = request.values.get("target", "data")
            goal = goals.get(request.values.get("goal"), "-")
            mode = request.values.get("mode", "")
            mode = mode if mode in modes else "lin"
            print(11, data)
            print(12, target)
            print(13, goal, mode)
            for i, dt in enumerate(data):
                payload = dict()
                payload[target] = [d.strip() for d in dt.split(",")]
                processing[i] = payload
        else:
            user_ids = request.json.get("users", "").split(",")
            user_ids = [int(user_id) for user_id in user_ids]
            info_keys = request.json.get("keys", "").split(",")
            target = request.json.get("target", None)
            goal = goals.get(request.json.get("goal"), "-")
            mode = request.json.get("mode", "")
            mode = mode if mode in modes else "lin"
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

        print(6, goal, mode, target, processing)

        decision = goal(mode, target, processing)
        print(7, decision)
        
        return jsonify({
            "success": True,
            "decision": decision
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

orderID = ""
decisions = []
counter = 0
choices = ""
participants = {}
original = ""

def notifyOriginal(original, decisions):
    print("~", decisions)
    req = requests.post("http://127.0.0.1:10101/think", {
        "data": "|".join([",".join(d) for d in decisions]),
        "goal": "-",
        "mode": "lin",
        "skip": "1"
    })
    decision = req.json().get("decision", "")

    requests.post("https://dedecus.serveo.net/sms/override", {
        "body": "Decision: %s" % decision,
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
    if participants.get(agent, 0) == 0 and word == 'order pizza':
        message = 'What choices?'
        participants[agent] = 1
    elif participants.get(agent, 0) == 1 and check(word):
        message = 'For how many?'
        choices = findall(pattern, word)
        participants[agent] = 2
    elif participants.get(agent, 0) == 2 and len(word) > 0:
        orderId = str(randint(1000,9999))
        message = "Order ID: " + orderId
        counter = word
        participants[agent] = 3
        original = agent
    elif participants.get(agent, 3) == 3 and word == orderId:
        message = 'List preferences in order: %s' % ", ".join(choices)
        participants[agent] = 4
    elif participants.get(agent, 3) == 4 and len(split(word)) == len(choices):
        decisions.append(split(word))
        message = 'Thank you!'
        participants[agent] = 0
        counter = int(counter) - 1
        if counter == 0:
            notifyOriginal(original, decisions)
            orderID = ""]
            decisions = []
            counter = 0
            choices = ""
            participants = {}
            original = ""
    else:
        message = 'Invalid'
    resp = MessagingResponse()
    resp.message(message)
    

    return str(resp)