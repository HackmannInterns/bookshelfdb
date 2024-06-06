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

def test_database_creation():
    directory = Path.cwd()
    database = Path(db)
    directory = os.path.join(directory, database)

    file_path = Path(directory)
    if file_path.exists():
        result = True
    else:
        result = False
    assert result is True

    os.remove(db)



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


    os.remove(db)
    print("Suck my nuts")



def test_read_books():

    read_books


def test_read_book():

    read_book


def test_update_book():

    update_book


def test_delete_book():

    delete_book
