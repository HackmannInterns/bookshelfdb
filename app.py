from flask import Flask, request, redirect, render_template
from time import sleep
import fetch
import db
from db import DB_LOCATION

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        book_id = request.form['book_id']
        year = request.form['year']
        publisher = request.form['publisher']
        print(f'Title: {title}\nAuthor: {author}\nID: {book_id}\nYear: {year}')
        db.create_book('Shelf 1', '123 Main St', 'Room 101', book_id, author, year,
                       title, publisher, None)
        return redirect("/")

    # Drawn from ScanApp/other
    elif 'isbn' in request.args:
        book_id = request.args['isbn']

        #
        title, author, publish_date, publisher = fetch.lookup_book_info(
            book_id)
        return render_template('form.html', title=title, author=author, book_id=book_id, year=publish_date, publisher=publisher)

    else:
        return render_template('form.html', title='', author='', book_id='', year='', publisher='')

# Init DB


if __name__ == '__main__':
    db.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
    # books = read_books()
    # for book in books:
    #     print(book)
