from http.client import OK
import json
from flask import Flask, jsonify, request, abort, Response, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import random
from flask_cors import CORS, cross_origin

file_path = os.path.abspath(os.getcwd())+"\\usernames.db"
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://ufecgkfjiqzgfa:ade59c25b70cd74b8bf574ae4958bb0b2ba649399333e8d9b42f864036c63129@ec2-44-195-162-77.compute-1.amazonaws.com:5432/d1ncuitteasauf'
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
cors = CORS(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.Column(db.Boolean)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    qualis = db.Column(db.Integer)
    age = db.Column(db.Integer)
    subjects = db.Column(db.String(50))
    bio = db.Column(db.String(300))
    prestige = db.Column(db.Float, default=random.random()*5)

    def __repr__(self) -> str:
        return '<User %r>' % self.username


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
    return jsonify(tutorList)


@app.errorhandler(401)
def AccessDenied(error):
    return Response('Incorrect credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
