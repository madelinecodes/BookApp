import os

from flask import Flask, session, redirect, render_template, request, jsonify
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


@app.route("/search", methods=['GET', 'POST'])
def search():
    if 'username' in session:
        if request.method == "POST":
            search = request.form.get("search")
            search_result = db.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE LOWER(:search)) OR (LOWER(title) LIKE LOWER(:search)) OR (author LIKE LOWER(:search)) LIMIT 10",
                { "search": '%' + search + '%'})
            if search_result.rowcount == 0:
                return render_template("none.html", message="we didnt find that search")
            elif search_result.rowcount >= 1:
                return render_template('book_list.html', result=search_result)
        else:
            return render_template('search.html')
    else:
        return redirect('/login')

@app.route("/book/<isbn>",  methods=['GET', 'POST']) 
def book_detail(isbn):
    review_list = db.execute("SELECT reviews.users, reviews.review, reviews.rating, books.isbn FROM reviews LEFT JOIN books ON reviews.isbn = books.isbn").fetchall()
    if 'username' in session and request.method == "POST":
        for review in review_list:
            if review.users == session['username'] and review.isbn == isbn:
                return 'Sorry, you can only review books once'

        isbn = db.execute("SELECT isbn FROM books WHERE isbn = :isbn LIMIT 1", {"isbn": isbn}).first()
        users = session['username']
        review = request.form.get("review")
        rating = request.form.get('rating')
        
        db.execute("INSERT INTO reviews (users, review, rating, isbn) VALUES (:users, :review, :rating, :isbn)", 
        {"users":users, "review":review, "rating":rating, "isbn":isbn.isbn})
        db.commit()
        return render_template("success.html")
    elif 'username' not in session and request.method == "POST":  
         return redirect('/login')
    else:
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 1", {"isbn": isbn}).first()
        return render_template('book_detail.html', review_list=review_list , book=book)

@app.route("/api/<isbn>",  methods=['GET']) 
def api_detail(isbn):
    book = dict()
    book_result = db.execute("SELECT title, author, pubyear, isbn FROM books WHERE isbn = :isbn", {"isbn":isbn}).first()
    book['title'] = book_result.title
    book['author'] = book_result.author
    book['pubyear'] = book_result.pubyear
    book['isbn'] = book_result.isbn

    review_result = db.execute("SELECT review, rating FROM reviews WHERE isbn = :isbn", {"isbn":isbn})
    review_count = 0
    review_sum = 0

    for review in review_result:
        if review.rating == None:
            continue
        review_count += 1
        review_sum += int(review.rating)
        average_rating = review_sum / review_count

    book['review_count'] = review_count
    book['average_score'] = average_rating

    return jsonify(book)

