
# import os
# from flask import Flask, session
# from flask_session import Session
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker

# app = Flask(__name__)

# # Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# # Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# # Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))


# @app.route("/")
# def index():
#     return "Project 1: TODO"



from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm, SearchForm, ReviewForm
from models import User, Book, Review, db
from import import import_books
from requests import get

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
#app.config["SECRET_KEY"] = "your_secret_key_here"

# Initialize DB and login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password_correction(form.password.data):
            login_user(user)
            return redirect(url_for('search'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_review/<isbn>', methods=['GET', 'POST'])
@login_required
def add_review(isbn):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(user_id=current_user.id, book_isbn=isbn, rating=form.rating.data, content=form.content.data)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('book_page', isbn=isbn))
    return render_template('add_review.html', form=form, isbn=isbn)

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = "%{}%".format(form.search.data)
        books = Book.query.filter(Book.title.ilike(query) | Book.author.ilike(query) | Book.isbn.ilike(query)).all()
        return render_template("search_results.html", books=books, form=form)
    return render_template("search.html", form=form)

@app.route("/book/<isbn>")
@login_required
def book_page(isbn):
    book = Book.query.get_or_404(isbn)
    reviews = Review.query.filter_by(book_isbn=isbn).all()
    return render_template("book.html", book=book, reviews=reviews)

@app.route('/get_book_details/<isbn>')
@login_required
def get_book_details(isbn):
    # Use Google Books API to fetch additional data
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = get(api_url)
    data = response.json()
    
    if data['totalItems'] > 0:
        book_data = data['items'][0]['volumeInfo']
        # Process book_data and merge with your local book details
    else:
        book_data = None

    return render_template('book_details.html', book_data=book_data)

if __name__ == '__main__':
    import_books()
    app.run(debug=True)
