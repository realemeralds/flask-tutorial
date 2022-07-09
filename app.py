from flask import Flask, jsonify, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# file_path = os.path.abspath(os.getcwd())+"\\usernames.db"

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgressql://ufecgkfjiqzgfa:ade59c25b70cd74b8bf574ae4958bb0b2ba649399333e8d9b42f864036c63129@ec2-44-195-162-77.compute-1.amazonaws.com:5432/d1ncuitteasauf'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return '<User %r>' % self.username


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/signup", methods=["GET", "POST"])
def signUp():
    if request.method == "POST":
        data = request.form.to_dict()
        print(data)
        if list(data.keys()) != ["username", "password"]:
            extra = "\n<p>Error...<p>"
        elif User.query.filter_by(username=data["username"]).first() == None:
            user = User(username=data["username"], password=data["password"])
            db.session.add(user)
            db.session.commit()
            extra = "\n<p><b>Success!<b><p>"
        else:
            extra = "\n<p>Error: Username is already taken<p>"

    return f'''
        <h1>Sign Up</h1>
        <form method="post">
            <label for="username">Username:</label><br>
            <input type=text name=username required><br>
            <label for="password">Password:</label><br>
            <input type=text name=password required><br>
            <input type=submit value=Signup>
        </form>{extra}
    '''


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form.to_dict()
        print(data)
        if list(data.keys()) != ["username", "password"]:
            abort(401)
        elif User.query.filter_by(username=data["username"]).first() != None:
            user = User.query.filter_by(username=data["username"]).first()
            userPw = user.password
            print(userPw, data["password"])
            if userPw == data["password"]:
                return jsonify({"type": "success",
                                "username": user.username,
                                "password": user.password,
                                "created": user.created,
                                "updated": user.updated})
            else:
                abort(401)

    extra = ""
    return f'''
        <h1>Login</h1>
        <form method="post">
            <label for="username">Username:</label><br>
            <input type=text name=username required><br>
            <label for="password">Password:</label><br>
            <input type=text name=password required><br>
            <input type=submit value=Login>
        </form>{extra}
    '''


@app.route("/changePassword", methods=["GET", "POST"])
def changePassword():
    if request.method == "POST":
        data = request.form.to_dict()
        print(data)
        if list(data.keys()) != ["username", "oldpassword", "newpassword"]:
            extra = "<br><p>Error.</p>"
            abort(401)
        elif User.query.filter_by(username=data["username"]).first() != None and User.query.filter_by(username=data["username"]).first().password == data["oldpassword"]:
            User.query.filter_by(username=data["username"]).first(
            ).password = data["newpassword"]
            db.session.commit()
            extra = "\n<p>Success!</p>"
        else:
            extra = "<br><p>Error.</p>"
            abort(401)

    return f'''
        <h1>Change Password</h1>
        <form method="post">
            <label for="username">Username:</label><br>
            <input type=text name=username required><br>
            <label for="password">Old Password:</label><br>
            <input type=text name=oldpassword required><br>
            <label for="password">New Password:</label><br>
            <input type=text name=newpassword required><br>
            <input type=submit value=Login>
        </form>{extra}
    '''


@app.errorhandler(401)
def AccessDenied(error):
    return Response('Incorrect credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


if __name__ == '__main__':
    app.run(debug=True)
