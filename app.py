from functools import wraps
from flask import Flask, request, redirect, render_template, session, send_file, url_for, jsonify, flash
from json.decoder import JSONDecodeError
from dotenv import load_dotenv
from os import getenv

import fetch
import db
import admin as admin_settings
import version
from permissions import get_permissions, is_permitted

app = Flask(__name__)

load_dotenv()
ADMIN_PASSWORD = getenv('BOOKSHELFDB_PASSWORD', 'changeme')
EDITOR_PASSWORD = getenv('BOOKSHELFDB_PASSWORD_EDITOR', 'changeme2')
app.secret_key = getenv('BOOKSHELFDB_SECRET_KEY', 'changeme')


class NoResultsFound(Exception):
    pass


class IncorrectPassword(Exception):
    pass


class BadFileType(Exception):
    pass


def send_to_login(permission):
    # Set permission (used to be session)
    perms = get_permissions()
    description = getattr(perms, f"desc_{permission}")
    required_permission = getattr(
        perms, f"req_perms_{permission}").name
    flash({'description': description,
          'required_permission': required_permission})

    return render_template('login.html')


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_permitted(permission):
                return send_to_login(permission)
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def inject_header_name_and_permissions():
    return {
        'header_name': admin_settings.get_settings().header_name,
        'Permission': get_permissions()
    }


@app.errorhandler(Exception)
def handle_error(error):
    error_message = str(error)
    return render_template('error.html', error_message=error_message)


@app.route('/search', methods=["GET", "POST"])
def mass_search():
    search_title = request.form.get('search_title', "")
    search_author = request.form.get('search_author', "")
    rows = fetch.search_by_author_title(search_author, search_title)
    books = [dict(b_id=-1,
                  identifier=row['olid'],
                  identifier_type='OLID',
                  title=row['title'],
                  author=row['authors'],
                  year=row['publish_date'],
                  publisher=row['publisher'],
                  subjects=row['subjects'],
                  description=None, ) for row in rows]
    if len(books) == 0:
        # return "No results Found", 401
        raise NoResultsFound("No Results Found")
    return render_template('rows.html', Books=books)


@app.route('/admin', methods=["GET", "POST"])
@permission_required('can_view_admin')
def admin():
    if 'address' in request.form and request.method == 'POST':
        new_add = str(request.form.get("address", ""))
        new_head = str(request.form.get("header_name", ""))
        new_view = bool(request.form.get("viewer", False))
        new_edit = bool(request.form.get("editor", False))
        admin_settings.update_yaml(
            visitor_can_add=new_view, editor_can_remove=new_edit, default_address=new_add, header_name=new_head)

    else:
        if request.args.get('q', "") == "clear":
            admin_settings.clear_cache_db()
        elif request.args.get('q', "") == "delete":
            admin_settings.delete_main_db()
            session['recent'] = []
        elif request.args.get('q', "") == "export":
            file_location = admin_settings.export_to_json()
            return send_file(file_location, as_attachment=True)
        elif request.args.get('q', "") == "import":
            if request.method == 'POST':
                try:
                    f = request.files['file']
                    admin_settings.import_from_json(f)
                    return redirect(url_for('admin'))
                except (UnicodeDecodeError, JSONDecodeError):
                    raise BadFileType(
                        "File upload failed, ensure the file is a .json exported from the application.")

    return render_template('admin.html',
                           Admin=admin_settings.get_settings(), Version=version.version_info)


@app.before_request
def before_request():
    if not request.path.startswith('/login') and not request.path.startswith('/static'):
        session['referer'] = request.full_path


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_password = request.form['password']
        if entered_password == ADMIN_PASSWORD:
            session['authenticated'] = 'Admin'
            return redirect(session['referer'])
        elif entered_password == EDITOR_PASSWORD:
            session['authenticated'] = 'Editor'
            return redirect(session['referer'])
        raise IncorrectPassword("Invalid Password")
    return render_template('login.html')


@app.route('/logout')
def logout():
    referer = request.headers.get('Referer')
    if referer is None:
        referer = '/'
    page = referer.split('/')[-1]
    if page == 'login' or page == 'logout':
        referer = '/'
    session.pop('authenticated', 'Viewer')
    session.pop('recent', None)
    # print(session.get('recent'))
    return redirect(referer)


@app.route('/scan')
def scan():
    return render_template('scan.html')


@app.route('/library')
@permission_required('can_view_library')
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
                  description=row[10], ) for row in rows]
    return render_template('rows.html', Books=books)


@app.route('/update', methods=["GET"])
def update():
    import time
    time.sleep(0.5)
    version.update_version_info()
    return jsonify({'newest': version.version_info.get('newest'), 'newest_link': version.version_info.get('newest_link')})
    # return jsonify({'newest': '10.9.8', 'newest_link': 'https://github.com/jellyfin/jellyfin/releases/tag/v10.9.8'})


@app.route('/library-recent')
def view2():
    rows = []
    for i in session.get("recent", []):
        rows.append(db.read_book(i))
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
                  description=row[10], ) for row in rows if row is not None]
    if books == []:
        session.pop('recent', None)
        return redirect(url_for('index'))
    return render_template('rows.html', Books=books)


@app.route('/delete')
def delete():
    if 'q' in request.args:
        if not is_permitted('can_edit', check_for_recent=int(request.args.get('q', -1))):
            # return redirect(url_for('login'))
            return send_to_login('can_remove')
        db.delete_book(request.args['q'])
    return redirect(url_for('view'))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'q' in request.args:
        if not is_permitted('can_edit', check_for_recent=int(request.args.get('q', -1))):
            # return redirect(url_for('login'))
            return send_to_login('can_edit')
        db_id = request.args['q']
        book = db.read_book(db_id)
        if book is None:
            return redirect(url_for('view'))
        return render_template('form.html', db_id=db_id,
                               title=book[8], author=book[6], book_id=book[4], id_type=book[5], year=book[7],
                               publisher=book[9], address=book[2], bookshelf=book[1], room=book[3], subjects=book[11],
                               edit=True)

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
        db.update_book(id=id, bookshelf_location=bookshelf, address=address, room=room, identifier=book_id,
                       identifier_type=id_type, author=author, year=year,
                       title=title, publisher=publisher, subjects=subjects)
        return redirect(url_for('view'))

    else:
        return redirect(url_for('view'))


@app.route('/add-book', methods=['GET', 'POST'])
@permission_required('can_add')
def add_book():
    if request.method == 'POST':
        session['address'] = request.form.get('address')
        session['room'] = request.form.get('room')
        session['bookshelf'] = request.form.get('bookshelf')

        # Manual entry via header "Add Book"
        if request.form.get('button_class') == 'manual':
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
            b_id = db.create_book(bookshelf, address, room, book_id, id_type, author, year,
                                  title, publisher, None, subjects)
            session.setdefault('recent', []).append(b_id)

            return render_template('form.html',
                                   address=admin_settings.get_settings().default_address)

    # isbn/lccn given
    elif (request.method == 'POST' and request.form.get('button_class') == 'auto') or ('isbn' in request.args or 'olid' in request.args):
        if 'isbn' in request.args:
            id_type = 'isbn'
            book_id = request.args['isbn']
        elif 'olid' in request.args:
            id_type = 'olid'
            book_id = request.args['olid']
        else:  # It's a auto
            id_type = request.form['id_type']
            book_id = request.form['search_id']
            session['id'] = request.form.get('id_type')

        title, author, publish_date, publisher, subjects = fetch.lookup_book_info(
            book_id, id_type)
        return render_template('form.html', address=admin_settings.get_settings().default_address,
                               title=title, author=author, book_id=book_id, id_type=id_type, year=publish_date, publisher=publisher, subjects=subjects)

    return render_template('form.html', address=admin_settings.get_settings().default_address)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/')
def index():
    return redirect(url_for('view'))


def init_all():
    version.version_check()
    db.init_db()


def run_flask(p=5000):
    init_all()
    app.run(port=p, host='0.0.0.0', debug=True)


def create_app():
    init_all()
    return app


if __name__ == '__main__':
    init_all()
    app.run(port=5000, host='0.0.0.0', debug=True)
