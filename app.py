from flask import Flask, request, redirect, render_template, session
import fetch
import db
from dotenv import load_dotenv
from os import getenv


app = Flask(__name__)

AUTO = True

load_dotenv()
PASSWORD = getenv('BOOKSHELFDB_PASSWORD', 'changeme')
app.secret_key = getenv('BOOKSHELFDB_SECRET_KEY', 'changeme')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('authenticated'):
        return redirect('/')
    if request.method == 'POST':
        entered_password = request.form['password']
        if entered_password == PASSWORD:
            session['authenticated'] = True
            return redirect('/')
        return 'Invalid password', 401
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect('/')

# When you hit the /scan page, under all circumstances, it renders scan.html
# nothing is passed in, scan.html works off JS
# scan.html is currently unreachable in the header unless hit directly as scanapp.org is better


@app.route('/scan')
def scan():
    return render_template('scan.html')


# When you hit the /view page, rows.html is rendered
# It creates and passes in a dictionary containing all the row data for a Book
# rows.html then processes this and creates a table, 1 row per DB entry
@app.route('/view')
def view():
    rows = db.read_books()
    books = [dict(b_id=row[0],
                  bookshelf_location=row[1],
                  address=row[2],
                  room=row[3],
                  identifier=fetch.correct_id(row[4], row[5])[0],
                  identifier_type=row[5],
                  author=row[6],
                  year=row[7],
                  title=row[8],
                  publisher=row[9],
                  subjects=row[11],
                  description=row[10],) for row in rows]
    return render_template('rows.html', SessionDict=session, Books=books)


@app.route('/delete')
def delete():
    if not session.get('authenticated'):
        return redirect('/login')
    if 'q' in request.args:
        db.delete_book(request.args['q'])
    return redirect('/view')


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if not session.get('authenticated'):
        return redirect('/login')
    # Start Editting
    if 'q' in request.args:
        session['q'] = True
        db_id = request.args['q']
        book = db.read_book(db_id)
        if book is None:
            return redirect('/view')
        return render_template('form.html', SessionDict=session, db_id=db_id, title=book[8], author=book[6], book_id=book[4], id_type=book[5], year=book[7], publisher=book[9], address=book[2], bookshelf=book[1], room=book[3], subjects=book[11], edit=True)

    if request.method == 'POST':
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
        subjects = request.form['subjects']
        db.update_book(id=id, bookshelf_location=bookshelf, address=address, room=room, identifier=book_id, identifier_type=id_type, author=author, year=year,
                       title=title, publisher=publisher, subjects=subjects)
        return redirect('/view')

    else:
        return redirect('/view')
    # End Editting

# When / is hit, form.html is rendered.  There are a lot of cases, as this page is used frequently
# When data is entered sutomatically, a button is valued at auto, which will fill the data using fetch
# When the page is first met, it is rendered with nothing else happening


@app.route('/', methods=['GET', 'POST'])
def index():
    # print(request.form.get('button_class'))
    session['autosubmit'] = AUTO
    session['autofilled'] = False

    # Manual entry
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
        subjects = request.form['subjects']
        session['address'] = address
        session['room'] = room
        session['bookshelf'] = bookshelf
        session['edit'] = False
        db.create_book(bookshelf, address, room, book_id, id_type, author, year,
                       title, publisher, None, subjects)
        return render_template('form.html', SessionDict=session)

    # isbn/lccn given
    elif request.method == 'POST' and request.form.get('button_class') == 'auto' or 'isbn' in request.args:
        if 'isbn' in request.args:
            id_type = 'isbn'
            book_id = request.args['isbn']
        else:
            id_type = request.form['id_type']
            book_id = request.form['search_id']
        title, author, publish_date, publisher, subjects = fetch.lookup_book_info(
            book_id, id_type)
        session['autofilled'] = True
        # print(title, author, publish_date, publisher)
        return render_template('form.html', SessionDict=session, title=title, author=author, book_id=book_id, id_type=id_type, year=publish_date, publisher=publisher, subjects=subjects)

    else:
        return render_template('form.html', SessionDict=session)


def run_flask(p=5000):
    db.init_db()
    app.run(port=p, host='0.0.0.0', debug=True)


def create_app():
    db.init_db()
    return app

if __name__ == '__main__':
    db.init_db()
    app.run(port=5000, host='0.0.0.0', debug=True)
