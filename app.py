from flask import Flask, request, redirect, render_template
import requests
import sqlite3
from os.path import isfile

DB_LOCATION = "testing.db"

app = Flask(__name__)


def lookup_book_info(isbn):
    if len(isbn) == 9:
        isbn = "0" + isbn

    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    print(url)
    response = requests.get(url)
    book_info = title = authors = publish_date = publisher = None
    # print(response)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        if f"ISBN:{isbn}" in data:
            book_info = data[f"ISBN:{isbn}"]
            title = book_info.get('title', 'Title not found')
            authors = ', '.join(author.get('name', 'Unknown Author')
                                for author in book_info.get('authors', []))
            publish_date = book_info.get(
                'publish_date', 'Publish date not found')
            publisher = ', '.join(publisher.get('name', 'Unknown Author')
                                  for publisher in book_info.get('publishers', []))
    return title, authors, publish_date, publisher


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        book_id = request.form['book_id']
        year = request.form['year']
        publisher = request.form['publisher']
        print(f'Title: {title}\nAuthor: {author}\nID: {book_id}\nYear: {year}')
        create_book('Shelf 1', '123 Main St', 'Room 101', book_id, author, year,
                    title, publisher, None)
        return redirect("/")

    # Drawn from ScanApp/other
    elif 'isbn' in request.args:
        book_id = request.args['isbn']

        #
        title, author, publish_date, publisher = lookup_book_info(book_id)
        return render_template('form.html', title=title, author=author, book_id=book_id, year=publish_date, publisher=publisher)

    else:
        return render_template('form.html', title='', author='', book_id='', year='', publisher='')

# Init DB


def init_db():
    if not isfile(DB_LOCATION):
        sql_create = '''
        CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bookshelf_location TEXT NULL,
        address TEXT NULL,
        room TEXT NULL,
        identifier TEXT NULL DEFAULT 'manual entry',
        author TEXT NULL,
        year INT NULL,
        title TEXT NULL,
        publisher TEXT NULL,
        description TEXT NULL,
        UNIQUE (id)
        );
        '''

        con = sqlite3.connect(DB_LOCATION)
        cur = con.cursor()
        cur.execute(sql_create)
        con.commit()
        con.close()
    else:
        # DB Exists
        pass

# Start CRUD
# Function to create a new record


def create_book(bookshelf_location, address, room, identifier, author, year, title, publisher, description):
    con = sqlite3.connect(DB_LOCATION)
    cur = con.cursor()
    cur.execute('''
        INSERT INTO books (bookshelf_location, address, room, identifier, author, year, title, publisher, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (bookshelf_location, address, room, identifier, author, year, title, publisher, description))
    con.commit()
    con.close()

# Function to read all records


def read_books():
    con = sqlite3.connect(DB_LOCATION)
    cur = con.cursor()
    cur.execute('SELECT * FROM books')
    rows = cur.fetchall()
    con.close()
    return rows

# Function to update a record


def update_book(id, bookshelf_location=None, address=None, room=None, identifier=None, author=None, year=None, title=None, publisher=None, description=None):
    con = sqlite3.connect(DB_LOCATION)
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
        values.append(author)
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

# Function to delete a record


def delete_book(id):
    con = sqlite3.connect("testing.db")
    cur = con.cursor()
    cur.execute('DELETE FROM books WHERE id = ?', (id,))
    con.commit()
    con.close()
# End CRUD


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
    # books = read_books()
    # for book in books:
    #     print(book)