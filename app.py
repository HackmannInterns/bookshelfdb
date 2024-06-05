from flask import Flask, request, redirect, render_template, session
from time import sleep
import fetch
import db
from db import DB_LOCATION

app = Flask(__name__)
app.secret_key = 'TESTING KEY'
AUTO = True


@app.route('/scan')
def scan():
    return render_template('scan.html')


@app.route('/view')
def view():
    if 'delete' in request.args:
        db.delete_book(request.args['delete'])
    rows = db.read_books()
    Books = [dict(b_id=row[0],
                  bookshelf_location=row[1],
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
    print(request.form.get('button_class'))
    session['autosubmit'] = AUTO
    session['autofilled'] = False
    if 'edit' in request.args:
        session['edit'] = True
        db_id = request.args['edit']
        book = db.read_book(db_id)
        return render_template('form.html', SessionDict=session, db_id=db_id, title=book[8], author=book[6], book_id=book[4], id_type=book[5], year=book[7], publisher=book[9], address=book[2], bookshelf=book[1], room=book[3])
        # return render_template('form.html', SessionDict=session)

    if request.method == 'POST' and request.form.get('button_class') == 'edit':
        id = request.form['db_id']
        title = request.form['title']
        author = request.form['author']
        book_id = request.form['book_id']
        id_type = request.form['id_type']
        year = request.form['year']
        publisher = request.form['publisher']
        address = request.form['address']
        room = request.form['room']
        bookshelf = request.form['bookshelf']
        db.update_book(id=id, bookshelf_location=bookshelf, address=address, room=room, identifier=book_id, identifier_type=id_type, author=author, year=year,
                       title=title, publisher=publisher)
        return redirect('/view')

    if request.method == 'POST' and request.form.get('button_class') == 'manual':
        title = request.form['title']
        author = request.form['author']
        book_id = request.form['book_id']
        id_type = request.form['id_type']
        year = request.form['year']
        publisher = request.form['publisher']
        address = request.form['address']
        room = request.form['room']
        bookshelf = request.form['bookshelf']
        print(session)
        if ('edit' not in session):
            print("edit not in session")
            session['edit'] = False
        if (not session['edit']):
            print(f'edit is {session["edit"]}')
            session['address'] = address
            session['room'] = room
            session['bookshelf'] = bookshelf
        session['edit'] = False
        db.create_book(bookshelf, address, room, book_id, id_type, author, year,
                       title, publisher, None)
        return render_template('form.html', SessionDict=session)

    elif request.method == 'POST' and request.form.get('button_class') == 'auto' or 'isbn' in request.args:
        if 'isbn' in request.args:
            id_type = 'isbn'
            book_id = request.args['isbn']
        else:
            id_type = request.form['id_type']
            book_id = request.form['search_id']
        title, author, publish_date, publisher = fetch.lookup_book_info(
            book_id, id_type)
        session['autofilled'] = True
        # print(title, author, publish_date, publisher)
        return render_template('form.html', SessionDict=session, title=title, author=author, book_id=book_id, id_type=id_type, year=publish_date, publisher=publisher)

    else:
        return render_template('form.html', SessionDict=session)


if __name__ == '__main__':
    db.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
    # books = read_books()
    # for book in books:
    #     print(book)
    # print(db.read_book(9))
