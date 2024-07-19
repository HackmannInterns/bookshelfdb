import sqlite3
import os

# consider putting everything in a temp file and nuking it after
from db import init_db, create_book, read_books, read_book, update_book, delete_book

db = "data/fake.db"
table_name = "books"

bookshelf = "shelf_location"
address = "address"
room = "room"
id = "ISBN"
numbers = "909090909090"
author = "John Whitney"
year = 2003
title = "book title"
publisher = "John Hackmann"
subjects = "Biography, Horor"

def clear_data():
    os.remove(db)



def delete_table(table_name, db):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Construct the SQL DROP TABLE statement
    sql_statement = f"DROP TABLE IF EXISTS {table_name};"

    # Execute the SQL statement to drop the table
    cursor.execute(sql_statement)

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()


def clear_table(table_name, db):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Construct the SQL DELETE statement without a condition
    sql_statement = f"DELETE FROM {table_name};"

    # Execute the SQL statement to delete all rows from the table
    cursor.execute(sql_statement)

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()


def table_exists(table_name, cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def test_database_creation():
    init_db(db)

    db_exists = os.path.exists(db)

    if db_exists:
        # Connect to the SQLite database
        conn = sqlite3.connect(db)

        # Create a cursor object
        cursor = conn.cursor()

        results = table_exists('books', cursor)

        # Close the cursor and connection
        cursor.close()
        conn.close()
    else:
        results = False

    assert db_exists is True
    assert results is True

    clear_data()


def test_create_book():
    init_db(db)

    create_book(None, None, None, None, None, None, None, title, None, None, None, db=db)
    create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, subjects, None, db=db)

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('SELECT * FROM books')
    rows = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    con.close()

    clear_table("books", db=db)

    assert len(rows) == 2

    clear_data()


def test_read_books():
    init_db(db)

    create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, None, subjects, db=db)

    rows = read_books(db)
    books = [dict(b_id=row[0],
                  bookshelf_location=row[1],
                  address=row[2],
                  room=row[3],
                  identifier=row[4],
                  identifier_type=row[5],
                  author=row[6],
                  year=row[7],
                  title=row[8],
                  publisher=row[9],
                  description=row[10],
                  subjects=row[11], ) for row in rows]

    for book in books:
        assert bookshelf == book['bookshelf_location']
        assert address == book['address']
        assert room == book['room']
        assert numbers == book['identifier_type']
        assert id == book['identifier']
        assert author == book['author']
        assert year == book['year']
        assert title == book['title']
        assert publisher == book['publisher']
        assert subjects == book['subjects']
        assert book['description'] is None

    clear_table("books", db=db)
    clear_data()


def test_read_book():
    init_db(db)

    create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, None, subjects, db=db)

    rows = read_books(db)
    books = [dict(b_id=row[0],
                  bookshelf_location=row[1],
                  address=row[2],
                  room=row[3],
                  identifier=row[4],
                  identifier_type=row[5],
                  author=row[6],
                  year=row[7],
                  title=row[8],
                  publisher=row[9],
                  description=row[10],
                  subjects=row[11], ) for row in rows]

    for book in books:
        b_id = book['b_id']

    row = read_book(b_id, db=db)

    assert b_id == row[0]
    assert bookshelf == row[1]
    assert address == row[2]
    assert room == row[3]
    assert id == row[4]
    assert numbers == row[5]
    assert author == row[6]
    assert year == row[7]
    assert title == row[8]
    assert publisher == row[9]
    assert subjects == row[11]
    assert row[10] is None

    clear_table("books", db=db)
    clear_data()


def test_update_book():
    init_db(db)

    create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, None, subjects, db=db)

    rows = read_books(db)
    books = [dict(b_id=row[0],
                  bookshelf_location=row[1],
                  address=row[2],
                  room=row[3],
                  identifier=row[4],
                  identifier_type=row[5],
                  author=row[6],
                  year=row[7],
                  title=row[8],
                  publisher=row[9],
                  subjects=row[11],
                  description=row[10], ) for row in rows]

    for book in books:
        b_id = book['b_id']

    f_bookshelf = "BOOKSHELF"
    f_address = "ADDRESS"
    f_room = "ROOM"
    f_id = "ID"
    f_numbers = "909090909090"
    f_author = "AUTHOR"
    f_year = 9999
    f_title = "TITLE"
    f_publisher = "PUBLISHER"
    f_subjects = "SUBJECTS"
    f_descriptor = "DESCRIPTOR"

    update_book(b_id, bookshelf_location=f_bookshelf, address=f_address, room=f_room, identifier=f_id, identifier_type=f_numbers, author=f_author, year=f_year, title=f_title, publisher=f_publisher, description=f_descriptor, subjects=f_subjects, db=db)

    row = read_book(b_id, db=db)

    assert b_id == row[0]
    assert f_bookshelf == row[1]
    assert f_address == row[2]
    assert f_room == row[3]
    assert f_id == row[4]
    assert f_numbers == row[5]
    assert f_author == row[6]
    assert f_year == row[7]
    assert f_title == row[8]
    assert f_publisher == row[9]
    assert f_descriptor == row[10]
    assert f_subjects == row[11]

    clear_table("books", db=db)
    clear_data()


def test_delete_book():
    init_db(db)

    create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, None, subjects, db=db)

    rows = read_books(db)
    books = [dict(b_id=row[0],
                  bookshelf_location=row[1],
                  address=row[2],
                  room=row[3],
                  identifier=row[4],
                  identifier_type=row[5],
                  author=row[6],
                  year=row[7],
                  title=row[8],
                  publisher=row[9],
                  subjects=row[11],
                  description=row[10], ) for row in rows]

    for book in books:
        b_id = book['b_id']

    delete_book(b_id, db=db)

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('SELECT * FROM books')
    rows = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    con.close()

    assert len(rows) == 0
    clear_data()
