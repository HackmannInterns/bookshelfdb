from pathlib import Path

import pytest
import sqlite3
import os

# consider putting everything in a temp file and nuking it after
from db import init_db, create_book, read_books, read_book, update_book, delete_book

db = "fake.db"

bookshelf = "shelf_location"
address = "address"
room = "room"
id = "ISBN"
numbers = "909090909090"
author = "John Whitney"
year = "2003"
title = "book title"
publisher = "John Hackmann"

@pytest.fixture
def set_up():

    init_db(db)

    #create_book(bookshelf_location, address, room, identifier, identifier_type, author, year, title, publisher, description)

def table_exists(table_name, cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def test_database_creation():
    init_db(db)

    # Connect to the SQLite database
    conn = sqlite3.connect('fake.db')

    # Create a cursor object
    cursor = conn.cursor()

    results = False
    # Check if a table named 'users' exists
    if table_exists('books', cursor):
        results = True
    else:
        results = False
    

    # Close the cursor and connection
    cursor.close()
    conn.close()

    yield db
    os.remove(db)

    assert results is True


def test_create_book():

    print(db)
    create_book(None, None, None, None, None, None, None, title, None, None, db)
    create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, None, db)

    print("before")
    print(read_books(db))
    print("after")

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('SELECT * FROM books')
    rows = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    con.close()

    yield db
    os.remove(db)



# def test_read_books():
# 
#     read_books
#
#
# def test_read_book():
#
#     read_book
#
#
# def test_update_book():
#
#     update_book
#
#
# def test_delete_book():
#
#     delete_book
