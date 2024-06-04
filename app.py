from flask import Flask, request, redirect, render_template
from time import sleep
import fetch
import db
from db import DB_LOCATION

app = Flask(__name__)


@app.route('/view')
def view():
    rows = db.read_books()
    Books = [dict(bookshelf_location=row[1],
                  address=row[2],
                  room=row[3],
                  identifier=row[4],
                  identifier_type=row[5],
                  author=row[6],
                  year=row[7],
                  title=row[8],
                  publisher=row[9],
                  description=row[10],) for row in rows]
    return render_template('rows.html', Books=Books)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and request.form.get('button_class') == 'manual':
        title = request.form['title']
        author = request.form['author']
        book_id = request.form['book_id']
        year = request.form['year']
        publisher = request.form['publisher']
        address = request.form['address']
        room = request.form['room']
        bookshelf = request.form['bookshelf']
        resp.set_cookie('address', address)
        resp.set_cookie('room', room)
        resp.set_cookie('bookshelf', bookshelf)
        if 'isbn' in request.args:
            id_type = 'isbn'
        elif 'lccn' in request.args:
            id_type = 'lccn'
        else:
            id_type = None
        db.create_book(bookshelf,address, room, book_id, id_type, author, year,
                       title, publisher, None)
        return redirect("/", Cookies=Cookies)

    elif request.method == 'POST' and request.form.get('button_class') == 'auto':
        return redirect(f"/?{request.form['id_type']}={request.form['search_id']}")

    # Drawn from ScanApp/other/manual entry
    elif 'lccn' in request.args or 'isbn' in request.args:
        if 'isbn' in request.args:
            book_id = request.args['isbn']
            id_type = 'isbn'
        elif 'lccn' in request.args:
            book_id = request.args['lccn']
            id_type = 'lccn'
        else:
            id_type = None
            book_id = None
        title, author, publish_date, publisher = fetch.lookup_book_info(
            book_id, id_type)
        # print(title, author, publish_date, publisher)
        return render_template('form.html', title=title, author=author, book_id=book_id, id_type=id_type, year=publish_date, publisher=publisher)

    else:
        return render_template('form.html', title='', author='', book_id='', year='', publisher='')


if __name__ == '__main__':
    db.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
    # books = read_books()
    # for book in books:
    #     print(book)
