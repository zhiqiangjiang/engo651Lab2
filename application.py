
import os
#from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

from flask import Flask, render_template, request, session, redirect
#from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

#import psycopg2
#app = Flask(__name__)
app = Flask(__name__, template_folder='templates')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# SQLAlchemy Base
Base = declarative_base()
# # User model with Flask-Login integration
# class User(UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#     registered_on = db.Column(db.DateTime, nullable=False)
# User model with Flask-Login integration
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)  # Use password hashing in practice
    registered_on = Column(DateTime, nullable=False, default=datetime.utcnow)

db = scoped_session(sessionmaker(bind=engine))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
# def index():
#     return "Project 1: TODO"
def index():
    return render_template('base.html')



#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/bookreview'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = 'your_secret_key_here'
#db = SQLAlchemy(app)


# ... (User model and registration/login routes similar to previous examples)

# Search route
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = '%' + request.form.get('query') + '%'
        result_proxy = db.engine.execute("""
            SELECT * FROM books 
            WHERE isbn LIKE %s OR title LIKE %s OR author LIKE %s
        """, (query, query, query))
        books = result_proxy.fetchall()
    return render_template('search_results.html', books=books)

# Book detail route
@app.route('/book/<isbn>')
def book_detail(isbn):
    result_proxy = db.engine.execute("""
        SELECT * FROM books WHERE isbn = %s
    """, (isbn,))
    book = result_proxy.fetchone()
    # Fetch reviews from a separate Reviews table (omitted for brevity)
    return render_template('book_detail.html', book=book)
# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        result = db.engine.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = result.fetchone()
        if existing_user:
            return "Username already exists!"

        # Insert new user
        db.engine.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate user
        result = db.engine.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        authenticated_user = result.fetchone()
        if authenticated_user:
            session['user_id'] = authenticated_user[0]
            return redirect(url_for('search'))

        return "Invalid credentials!"

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Add review route
@app.route('/book/<isbn>/add_review', methods=['POST'])
def add_review(isbn):
    if 'user_id' in session:
        user_id = session['user_id']
        rating = request.form['rating']
        comment = request.form['comment']

        # Insert review into Reviews table (assuming it has user_id, isbn, rating, comment columns)
        db.engine.execute("INSERT INTO reviews (user_id, isbn, rating, comment) VALUES (%s, %s, %s, %s)",
                          (user_id, isbn, rating, comment))
        conn.commit()

        return redirect(url_for('book_detail', isbn=isbn))

    return redirect(url_for('login'))

# No need for teardown function as SQLAlchemy manages connections

if __name__ == '__main__':
    app.run(debug=True)



# @app.route('/get_book_details/<isbn>')
# @login_required
# def get_book_details(isbn):
#     # Use Google Books API to fetch additional data
#     api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
#     response = get(api_url)
#     data = response.json()
    
#     if data['totalItems'] > 0:
#         book_data = data['items'][0]['volumeInfo']
#         # Process book_data and merge with your local book details
#     else:
#         book_data = None

#     return render_template('book_details.html', book_data=book_data)


