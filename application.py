
import os
from flask_session import Session
from sqlalchemy import create_engine,Column, Integer, String, DateTime, MetaData, Table,text
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request, session, redirect, url_for, flash, Blueprint, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, SearchForm, ReviewForm
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash,check_password_hash

#app = Flask(__name__)
app = Flask(__name__, template_folder='templates')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'mysecretkey'  

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# SQLAlchemy Base
Base = declarative_base()

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
    return db.query(User).get(int(user_id))

# Register route
import hashlib
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Hash the password 
        password_hashed = generate_password_hash(password, method='pbkdf2:sha256')

        # Execute a raw SQL query to check if the username already exists
        result = db.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        existing_user = result.fetchone()

        if existing_user:
            # Username already exists
            return render_template('register.html', form=form, error_message="Your input username already taken.")
        
        # Get the current timestamp
        registered_on = datetime.now()

        # Insert the new user with the hashed password and the current timestamp
        insert_query = text("""
            INSERT INTO users (username, password_hash, registered_on)
            VALUES (:username, :password_hash, :registered_on)
        """)
        db.execute(insert_query, {
            "username": username,
            "password_hash": password_hashed,
            "registered_on": registered_on
        })
        
        # Commit the transaction
        db.commit()
        flash("User registered successfully!")
        # Redirect to login page
        return render_template('login.html', form=form)

    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Fetch the user based on the entered username
        #user = User.query.filter_by(username=form.username.data).first()
        user = db.query(User).filter_by(username=form.username.data).first()

        # Check if the user exists and the password matches
        if user and check_password_hash(user.password_hash, form.password.data):
            # Successful login logic, e.g., log the user in, set session, etc.
            login_user(user)
            session['user_id'] = user.id

            #flash('Logged in successfully!')
            return redirect(url_for('search'))
            #return render_template('search.html', form=form)


        else:
            # Invalid credentials
            flash('Invalid username or password.')

    return render_template('login.html', form=form)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))

# Index route
@app.route("/")
def index():
    return render_template('base.html')

# Search route
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    books = []

    if form.validate_on_submit():
        isbn = form.isbn.data
        title = form.title.data
        author = form.author.data

        if not (isbn or title or author):
            flash("Please fill in at least one field.")
            return render_template('search.html', form=form)

        # Build the WHERE clause dynamically based on the input
        conditions = []
        params = {}

        if isbn:
            conditions.append("books.isbn = :isbn")
            params["isbn"] = isbn

        if title:
            conditions.append("books.title LIKE :title")
            params["title"] = f"%{title}%"

        if author:
            conditions.append("books.author LIKE :author")
            params["author"] = f"%{author}%"
        

        # Combine the conditions
        if conditions:
            where_clause = " AND ".join(conditions)
        else:
            # If no conditions are present, we cannot perform a search
            return render_template('search.html', form=form)

        # Execute the raw SQL query
        query = text(f"""
            SELECT * FROM books
            WHERE {where_clause}
        """)

        result = db.execute(query, params)
      
        # Convert the result to a list of dictionaries
        #print(result)
        books = [{'isbn': row[0], 'title': row[1], 'author': row[2], 'year':row[3]} for row in result]

        return render_template('search_results.html', books=books, form=form)

    return render_template('search.html', form=form)



# Book detail route
bp = Blueprint('book_detail', __name__)
@bp.route('/book/<string:isbn>')
def book_detail(isbn):
    # Query for book details
    book_query = text("""
        SELECT isbn, title, author, year
        FROM books
        WHERE isbn = :isbn
    """)
    book_result = db.execute(book_query, {'isbn': isbn}).fetchone()

    # Check if book exists
    if book_result is None:
         abort(404)

    import requests
    # Define the base URL for the Google Books API
    base_url = "https://www.googleapis.com/books/v1/volumes"

    # Add the ISBN as a search term
    params = {
        'q': f'isbn:{isbn}',
        'key': 'AIzaSyAu0x1QxQgJwm75g1RHk3P-KaHBpHKp4i0', 
    }

    book_data = {}
    try:
        # Make the GET request
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        # Parse the JSON data
        book_data = response.json()
    except requests.exceptions.HTTPError as error:
        print(f"HTTP error occurred: {error}")
        #return render_template('book_detail.html', book=book_result, reviews=reviews,review_form=review_form)
   
    book_info = None
    average_rating = 0
    ratingsCount = 0

    if book_data['items']:
        book_info = book_data['items'][0]
        average_rating = book_info['volumeInfo'].get('averageRating')
        ratingsCount = book_info['volumeInfo'].get('ratingsCount')  
        #print(f"avrating: {average_rating}")
    else:
        flash("Book Not Found From Google BookAPI.") 
    

    book_details = {'isbn': book_result[0], 'title': book_result[1], 'author': book_result[2], 'year':book_result[3], 'average_rating':average_rating, 'ratingsCount':ratingsCount}

    # Instantiate the ReviewForm
    review_form = ReviewForm()


    # Query for book reviews
    reviews_query = text("""
        SELECT rating, content
        FROM reviews
        WHERE book_isbn = :isbn
    """)
    reviews_result = db.execute(reviews_query, {'isbn': isbn}).fetchall()
    reviews = [{'rating':row[0],'content':row[1]} for row in reviews_result]

    return render_template('book_detail.html', book=book_details, reviews=reviews,review_form=review_form)
 
# Add Review route
@bp.route('/book/<string:isbn>/add_review', methods=['POST'])
@login_required # This ensures that only logged in users can access this route
def add_review(isbn):
    form = ReviewForm()
    if form.validate_on_submit():
        # Process the form data and add the review to the database using the isbn
      
        user_id = current_user.get_id()
        rating = request.form['rating']
        content = request.form['content']
        # Get the current timestamp
        created_on = datetime.now()

        # Check if the user has already reviewed this book using raw SQL
        query = text("""
        SELECT 1 FROM reviews WHERE user_id = :user_id AND book_isbn = :book_isbn LIMIT 1; """)
        result = db.execute(query, {'user_id': user_id, 'book_isbn': isbn})

        if result.fetchone():  # If there's any row returned, the user has already reviewed this book
            flash('You have already reviewed this book.', 'error')
            return redirect(url_for('book_detail.book_detail', isbn=isbn))
        
        # Insert review into Reviews table (assuming it has user_id, isbn, rating, comment columns)
        query = text("""
        INSERT INTO reviews (user_id, book_isbn, rating, content, created_on)
        VALUES (:user_id, :book_isbn, :rating, :content, :created_on)   """)
       
        db.execute(query, {'user_id': user_id, 'book_isbn': isbn, 'rating': rating, 'content': content, 'created_on': created_on})
        db.commit()
        flash('Your review was successfully added!', 'success')
        return redirect(url_for('book_detail.book_detail', isbn=isbn))
    else:
        # If the form is invalid, re-render the book detail page with the form errors
        #book_details = get_book_by_isbn(book_isbn)  # Fetch book again for re-rendering the page
        #return render_template('book_detail.html', book=book_details, reviews=..., review_form=form)
        flash('Invalid Form')
        return redirect(url_for('book_detail.book_detail', isbn=isbn))



# No need for teardown function as SQLAlchemy manages connections
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)




