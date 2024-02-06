# Project 1: Book Review Website 
Project Description: 
This project is a Flask-based web application for users to browse books, post reviews, register/login/logout account and use a 3rd-party API by Google Books to pull in ratings from a broader audience.

File Structure & Explanation:
* import.py: define and create required database tables. import the books from csv into database,
* application.py: the main entry point of the application, where Flask routes are defined and implemented. User unique review can be submitted. Google Books API is used to display the average rating and number of ratings.
* forms.py: contains the Flask-WTF form classes used throughout the application.
* templates/base.html: The base template providing common layout and styles.
* templates/login.html and register.html: Templates for user authentication.
* templates/search.html: A page allowing users to search for books and display results.
* templates/search_results.html: A page to display search results of book list.
* templates/book_detail.html: A page showing detailed information about a book, google book api information and its database reviews. 

Additional Information:
* The application uses Flask-Login for session management and user authentication.
* Google Books API is applied for average rating and number of ratings data.
* Raw SQL commands via SQLAlchemy’s execute method is applied according to project requirement.
* A JSON website API endpoint is implemented to provide book detailed information based on isbn parameter in the GET request.
* Users' passwords are hashed using Werkzeug's secure password hashing utilities.
* Session is applied to store user_id for insert user review
