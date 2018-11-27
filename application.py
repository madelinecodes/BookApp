import os

from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not ("postgres://yonqdsmbstzzvf:911fa8f0e419f903e0458cc89fb3933954ec0ceffd16bff11d1bdf77cc3d75b2@ec2-54-75-231-3.eu-west-1.compute.amazonaws.com:5432/ded71cdjkufg4o"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://yonqdsmbstzzvf:911fa8f0e419f903e0458cc89fb3933954ec0ceffd16bff11d1bdf77cc3d75b2@ec2-54-75-231-3.eu-west-1.compute.amazonaws.com:5432/ded71cdjkufg4o")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if 'username' in session:
        return 'Logged in as ' + session['username']
    else:
        return 'You are not logged in!'

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username" : username, "password": password})
        db.commit()
        session['username'] = username
        return redirect('/')
    else:
        return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/')
        #redirect to index 
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        login_result = db.execute("SELECT * FROM users WHERE username = :username AND password = :password ",
            {"username": username, "password": password})

        if login_result.rowcount == 0:
                return render_template("register.html", message="You're not currently registered")
        elif login_result.rowcount == 1:
            session['username'] = username
            return 'Logged in as ' + session['username']
            #thats their thingy so we need to start a session for them
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    if 'username' in session:
        session.pop('username', None)
    return 'Logged out!'