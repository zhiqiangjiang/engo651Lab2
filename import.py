import csv
from models import Book, db

def import_books():
    with open("books.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            book = Book(
                isbn=row['isbn'],
                title=row['title'],
                author=row['author'],
                publication_year=int(row['year'])
            )
            db.session.add(book)
        db.session.commit()