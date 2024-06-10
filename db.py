import os
from os.path import isfile
import sqlite3

DB_LOCATION = "data/bookshelf.db"

# Init DB if it doesn't exist


def init_db(db=DB_LOCATION):
    filename = db
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not isfile(db):
        sql_create = '''
        CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bookshelf_location TEXT NULL,
        address TEXT NULL,
        room TEXT NULL,
        identifier TEXT NULL DEFAULT 'manual entry',
        identifier_type TEXT NULL DEFAULT 'manual entry',
        author TEXT NULL,
        year INT NULL,
        title TEXT NULL,
        publisher TEXT NULL,
        description TEXT NULL,
        subjects TEXT NULL,
        UNIQUE (id)
        );
        '''

        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(sql_create)
        con.commit()
        con.close()
    else:
        # DB Exists
        pass

# Start CRUD
# Function to create a new record


def create_book(bookshelf_location, address, room, identifier, identifier_type, author, year, title, publisher, description, db=DB_LOCATION):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('''
        INSERT INTO books (bookshelf_location, address, room, identifier, identifier_type, author, year, title, publisher, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (bookshelf_location, address, room, identifier, identifier_type, author, year, title, publisher, description))
    con.commit()
    con.close()

# Function to read all records


def read_books(db=DB_LOCATION):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('SELECT * FROM books')
    rows = cur.fetchall()
    con.close()
    return rows

# Function to read specific record


def read_book(id, db=DB_LOCATION):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('SELECT * FROM books WHERE id = ?', (id,))
    row = cur.fetchone()
    con.close()
    return row

# Function to update a record


def update_book(id, bookshelf_location=None, address=None, room=None, identifier=None, identifier_type=None, author=None, year=None, title=None, publisher=None, description=None, db=DB_LOCATION):
    con = sqlite3.connect(db)
    cur = con.cursor()
    update_query = 'UPDATE books SET '
    update_fields = []
    values = []

    if bookshelf_location is not None:
        update_fields.append('bookshelf_location = ?')
        values.append(bookshelf_location)
    if address is not None:
        update_fields.append('address = ?')
        values.append(address)
    if room is not None:
        update_fields.append('room = ?')
        values.append(room)
    if identifier is not None:
        update_fields.append('identifier = ?')
        values.append(identifier)
    if author is not None:
        update_fields.append('author = ?')
        values.append(author)
    if year is not None:
        update_fields.append('year = ?')
        values.append(year)
    if title is not None:
        update_fields.append('title = ?')
        values.append(title)
    if publisher is not None:
        update_fields.append('publisher = ?')
        values.append(publisher)
    if description is not None:
        update_fields.append('description = ?')
        values.append(description)

    update_query += ', '.join(update_fields) + ' WHERE id = ?'
    values.append(id)

    cur.execute(update_query, values)
    con.commit()
    con.close()


def delete_db(db=DB_LOCATION):
    os.remove(db)

# Function to delete a record

def delete_book(id, db=DB_LOCATION):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('DELETE FROM books WHERE id = ?', (id,))
    con.commit()
    con.close()
# End CRUD
