from http.client import OK
import json
from flask import Flask, jsonify, request, abort, Response, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
import os
from datetime import datetime
import random
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message
import math

file_path = os.path.abspath(os.getcwd())+"\\usernames.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
# app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://gzsvtmkpsajnro:35384e3e400bbc9166483f4c2a5e45af4d55efd1429d083fa46f96917a0b3421@ec2-52-73-184-24.compute-1.amazonaws.com:5432/d8rc6an89uh6mq'
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'bf56e8b6c3b351'
app.config['MAIL_PASSWORD'] = 'cea77bd82ecc97'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
db = SQLAlchemy(app)
cors = CORS(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.Column(db.Boolean)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    qualis = db.Column(db.Integer)
    pastExp = db.Column(db.Integer, default=0)
    age = db.Column(db.Integer)
    subjects = db.Column(db.String(50))
    bio = db.Column(db.String(300))
    ratings = db.Column(db.Integer, default=2.5)

    @hybrid_property
    def prestige(self):
        if self.teacher == True:
            if type(self.subjects == "int"):
                self.subjects = json.dumps([self.subjects, ])
            return (self.ratings / 3 + max(self.pastExp, 5) / 5 + (self.qualis - 3) / 3 + (1 / math.log2(len(json.loads(self.subjects))+1)) + max(self.age, 30) / 30)

    def __repr__(self) -> str:
        return '<User %r>' % self.username


@app.route("/email/<sender>/<receiver>", methods=["GET", "POST"])
@cross_origin()
def index(sender, receiver):
    msg = Message('CasuTuition Connection',
                  sender='casuTuition@mailtrap.io', recipients=['example@mailtrap.io', receiver])
    msg.body = f"Good afternoon, {sender} (email address: {User.query.filter_by(username=sender).first().email}) has requested to contact you on CasuTuition!"
    mail.send(msg)
    return jsonify("Message sent!")


@app.route("/signup", methods=["GET", "POST"])
@cross_origin()
def signUp():
    if request.method == "POST":
        data = request.json
        print(data)
        if User.query.filter_by(username=data["username"]).first() == None:
            if data["teacher"] == "true":
                user = User(teacher=True, username=data["username"],
                            password=data["password"], email=data["email"], qualis=data["qualis"], subjects=data["subjects"], bio=data["bio"], age=data["age"])

            else:
                user = User(teacher=False, username=data["username"],
                            password=data["password"], email=data["email"])
            db.session.add(user)
            db.session.commit()
            response = jsonify({"order_id": 123, "status": "shipped"})
            return response
        else:
            return "username already exists"
    return "Hello!"


@app.route("/login", methods=["GET", "POST"])
@cross_origin()
def login():
    print(request.__dict__)
    if request.method == "POST":
        data = request.json
        print(data)
        if User.query.filter_by(username=data["username"]).first() != None:
            user = User.query.filter_by(username=data["username"]).first()
            userPw = user.password
            print(userPw, data["password"])
            if userPw == data["password"]:
                return jsonify({"type": "success",
                                "username": user.username,
                                "password": user.password})
        else:
            abort(401)
    abort(401)


@app.route("/tutor")
def tutor():
    tutors = User.query.filter_by(teacher=True).all()
    tutorList = []
    for user in tutors:
        adding = {"username": user.username, "interest": json.loads(user.subjects),
                  "quali": user.qualis, "prestige": round(user.prestige, 2), "bio": user.bio, "email": user.email}
        tutorList.append(adding)
    sortedTutorList = sorted(tutorList, key=lambda d: d['prestige'])
    return jsonify(sortedTutorList)


@app.errorhandler(401)
def AccessDenied(error):
    return Response('Incorrect credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
