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
        return 'Try the home page.'
    else:
        return render_template('register.html')
