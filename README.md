# Project 1: Book Review Website 
Project Description: 
This project is a Flask-based web application for users to browse books, post reviews, and register/login/logout account. 

File Structure & Explanation:
* import.py: define and create required database tables. import the books from csv into database,
* application.py: the main entry point of the application, where Flask routes are defined and implemented.
* forms.py: contains the Flask-WTF form classes used throughout the application.
* templates/base.html: The base template providing common layout and styles.
* templates/login.html and register.html: Templates for user authentication.
* templates/search.html: A page allowing users to search for books and display results.
* templates/search_results.html: A page to display search results of book list.
* templates/book_detail.html: A page showing detailed information about a book and its reviews.

Additional Information:
* The application uses Flask-Login for session management and user authentication.
* CSRF protection is enabled through Flask-WTF.
* Raw SQL commands via SQLAlchemy’s execute method is applied according to project requirement.
* Users' passwords are hashed using Werkzeug's secure password hashing utilities.
* Session is applied to store user_id for insert user review
