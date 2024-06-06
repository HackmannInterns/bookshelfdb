import pytest
import sqlite3


from db import init_db, create_book, read_books, read_book, update_book, delete_book

DB_LOCATION = "fake.db"

bookshelf = "shelf_location"
address = "address"
room = "room"
Id = "ISBN"
numbers = "909090909090"
author = "John Whitney"
year = "2003"
title = "birth"
publisher = "John Hackmann"

@pytest.fixture
def set_up():
    init_db()



# create_book(bookshelf_location, address, room, identifier, identifier_type, author, year, title, publisher, description)
# def test_create_book():
#     create_book(bookshelf, address, room, Id, numbers, author, year, title, publisher, None)


# def test_read_books():
#     read_books


# def test_read_book():
#     read_book


# def test_update_book():
#     update_book


# def test_delete_book():
#     delete_book
