import csv
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, DateTime, Boolean, Float, ForeignKey, insert
from sqlalchemy.orm import sessionmaker

# Database connection string
DATABASE_URL = 'postgresql://myuser:mypassword@localhost:5432/mydatabase'

# Create metadata and define table schemas
metadata = MetaData()

# Users table (no data to import, but creating the table anyway)
users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, unique=True, nullable=False),
    Column('password_hash', String, nullable=False),
    Column('registered_on', DateTime, nullable=False)
)

# Books table
books_table = Table(
    'books', metadata,
    Column('isbn', String(13), primary_key=True),
    Column('title', String, nullable=False),
    Column('author', String, nullable=False),
    Column('year', String, nullable=False)
)

# Reviews table (no data to import, but creating the table anyway)
reviews_table = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('book_isbn', String(13), ForeignKey('books.isbn'), nullable=False),
    Column('content', String, nullable=False),
    Column('rating', Float, nullable=False),
    Column('created_on', DateTime, nullable=False)
)

# Establish a connection to the database
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

def import_books_from_csv(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows_to_insert = []
        for row in reader:
            rows_to_insert.append({
                'isbn': row['isbn'],
                'title': row['title'],
                'author': row['author'],
                'year': row['year']
            })

        # Bulk insert the rows
        stmt = insert(books_table)
        session.execute(stmt, rows_to_insert)
        session.commit()
        print(f"{reader.line_num} books imported.")

if __name__ == "__main__":
    csv_file_path = "books.csv"
    import_books_from_csv(csv_file_path)
    session.close()