from enum import Enum

from flask import Flask, request, redirect, render_template, session, send_file
import fetch
import db
import admin as admin_settings
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)
AUTO = True

load_dotenv()
ADMIN_PASSWORD = getenv('BOOKSHELFDB_PASSWORD', 'changeme')
EDITOR_PASSWORD = getenv('BOOKSHELFDB_PASSWORD_EDITOR', 'changeme2')
app.secret_key = getenv('BOOKSHELFDB_SECRET_KEY', 'changeme')


# Maybe goes in new class, idk

class Auth(Enum):
    Viewer = 0
    Editor = 1
    Admin = 2


def get_permissions(is_recent=False):
    user_type = Auth[session.get('authenticated', 'Viewer')]
    # print(user_type)
    yaml_settings = admin_settings.get_settings()

    class Permissions:
        # admin=2 editor=1 viewer=0

        # setting add perms
        req_perms_add = Auth['Viewer'] if user_type is Auth['Viewer'] and yaml_settings.visitor_can_add else Auth[
            'Editor']
        desc_can_add = 'You cannot add with your current authentication level'
        can_add = False
        if user_type.value >= Auth['Editor'].value or yaml_settings.visitor_can_add:
            can_add = True

        # setting remove perms
        if (user_type == Auth['Editor'] and yaml_settings.editor_can_remove) or (
                user_type == Auth['Editor'] and is_recent):
            req_perms_remove = Auth['Editor']
        elif user_type is Auth['Viewer'] and is_recent:
            req_perms_remove = Auth['Viewer']
        else:
            req_perms_remove = Auth['Admin']
        desc_can_remove = 'You cannot remove with your current authentication level'
        can_remove = False
        if user_type == Auth['Admin'] or (user_type == Auth['Editor'] and yaml_settings.editor_can_remove) or (
                user_type == Auth['Editor']
                and is_recent) or (user_type is None and is_recent):
            can_remove = True

        # setting edit perms
        req_perms_edit = Auth['Viewer'] if user_type is None and is_recent else Auth['Editor']
        desc_can_edit = 'You cannot edit with your current authentication level'
        can_edit = ((user_type.value >= Auth['Editor'].value) or ((user_type.value >= Auth['Viewer'].value) and is_recent))

        # setting admin perms
        req_perms_admin = Auth['Admin']
        desc_can_view_admin = 'You cannot view admin with your current authentication level'
        can_view_admin = user_type.value >= Auth['Admin'].value

        # setting viewing perms
        req_perms_view_views = Auth['Viewer']
        desc_can_view_views = 'You cannot view the views page with your current authentication level'
        can_view_views = user_type.value >= Auth['Viewer'].value

    return Permissions()


@app.route('/search', methods=["GET", "POST"])
def mass_search():
    search_title = session['search_title']
    search_author = session['search_author']
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
        return "No results Found", 401
    return render_template('rows.html', header_name=admin_settings.get_settings().header_name, Books=books)


@app.route('/admin', methods=["GET", "POST"])
def admin():
    if not get_permissions().can_view_admin:
        session['description'] = get_permissions().desc_can_view_admin
        session['required_permission'] = get_permissions().req_perms_admin.name
        return redirect('/login')
    if 'address' in request.form and request.method == 'POST':
        new_add = str(request.form.get("address", ""))
        new_head = str(request.form.get("header_name", ""))
        new_view = bool(request.form.get("viewer", False))
        new_edit = bool(request.form.get("editor", False))
        admin_settings.update_yaml(
            visitor_can_add=new_view, editor_can_remove=new_edit, default_address=new_add, header_name=new_head)

    else:
        if 'q' in request.args and request.args['q'] == "clear":
            admin_settings.clear_cache_db()
        elif 'q' in request.args and request.args['q'] == "delete":
            admin_settings.delete_main_db()
            session['recent'] = []
        elif 'q' in request.args and request.args['q'] == "export":
            file_location = admin_settings.export_to_json()
            return send_file(file_location, as_attachment=True)
        elif 'q' in request.args and request.args['q'] == "import":
            if request.method == 'POST':
                try:
                    f = request.files['file']
                    admin_settings.import_from_json(f)
                    return redirect('/admin')
                except:
                    return "File upload failed, ensure the file is a .json and exported from our application"

    return render_template('admin.html', header_name=admin_settings.get_settings().header_name,
                           Admin=admin_settings.get_settings())


@app.route('/login', methods=['GET', 'POST'])
def login():


    session['insufficient_perm'] = 'true'
    if Auth[session['required_permission']].value <= Auth[session.get('authenticated', 'Viewer')].value:
        session['insufficient_perm'] = 'false'
    referer = request.headers.get('Referer')
    if referer is None:
        referer = '/'
    page = referer.split('/')[-1]
    if page == 'login' or page == 'logout':
        referer = '/'
    if request.method == 'POST':
        entered_password = request.form['password']
        if entered_password == ADMIN_PASSWORD:
            session['authenticated'] = 'Admin'
            return redirect(referer)
        elif entered_password == EDITOR_PASSWORD:
            session['authenticated'] = 'Editor'
            return redirect(referer)
        return 'Invalid password', 401
    return render_template('login.html', header_name=admin_settings.get_settings().header_name)


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


# When you hit the /scan page, under all circumstances, it renders scan.html
# nothing is passed in, scan.html works off JS
# scan.html is currently unreachable in the header unless hit directly as scanapp.org is better


@app.route('/scan')
def scan():
    return render_template('scan.html', header_name=admin_settings.get_settings().header_name)


# When you hit the /view page, rows.html is rendered
# It creates and passes in a dictionary containing all the row data for a Book
# rows.html then processes this and creates a table, 1 row per DB entry
# TODO: implement permissions
@app.route('/view')
def view():
    if not get_permissions().can_view_views:
        session['description'] = get_permissions().desc_can_view_views
        session['required_permission'] = get_permissions().req_perms_view_views.name
        return redirect('/login')
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
    return render_template('rows.html', header_name=admin_settings.get_settings().header_name, Books=books)


@app.route('/view-recent')
# TODO: implement permissions
def view2():
    if 'recent' not in session:
        session['recent'] = []
    rows = []
    # print(session["recent"])
    for i in session["recent"]:
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
    return render_template('rows.html', header_name=admin_settings.get_settings().header_name, Books=books)


@app.route('/delete')
def delete():
    if 'recent' not in session:
        session['recent'] = []
    can_remove = get_permissions(is_recent=(
            int(request.args.get('q', 0)) in session['recent'])).can_remove
    if 'q' in request.args and can_remove:
        db.delete_book(request.args['q'])
    elif 'q' in request.args and not can_remove:
        session['description'] = get_permissions().desc_can_remove
        session['required_permission'] = get_permissions().req_perms_remove.name
        return redirect('/login')
    return redirect('/view')


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'recent' not in session:
        session['recent'] = []

    can_edit = get_permissions(is_recent=(int(request.args.get('q', 0)) in session['recent'])).can_edit
    if 'q' in request.args and can_edit:
        session['q'] = True
        db_id = request.args['q']
        book = db.read_book(db_id)
        if book is None:
            return redirect('/view')
        return render_template('form.html', header_name=admin_settings.get_settings().header_name, db_id=db_id,
                               title=book[8], author=book[6], book_id=book[4], id_type=book[5], year=book[7],
                               publisher=book[9], address=book[2], bookshelf=book[1], room=book[3], subjects=book[11],
                               edit=True)
    elif 'q' in request.args and not can_edit:
        session['description'] = get_permissions().desc_can_edit
        session['required_permission'] = get_permissions().req_perms_edit.name
        return redirect("/login")

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
        return redirect('/view')

    else:
        return redirect('/view')
    # End Editting


# When /submit is hit, form.html is rendered.  There are a lot of cases, as this page is used frequently
# When data is entered sutomatically, a button is valued at auto, which will fill the data using fetch
# When the page is first met, it is rendered with nothing else happening

# TODO: implement permissions & change page


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if not get_permissions().can_add:
        session['description'] = get_permissions().desc_can_add
        session['required_permission'] = get_permissions().req_perms_add.name
        return redirect('/login')
    # print(session["recent"])
    # session["recent"] = []
    # print(request.form.get('button_class'))
    session['autosubmit'] = AUTO
    session['autofilled'] = False

    if request.method == 'POST' and request.form.get('button_class') == 'title_author_search':
        session['search_title'] = request.form.get('search_title', "")
        session['search_author'] = request.form.get('search_author', "")
        return redirect("/search")

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
        b_id = db.create_book(bookshelf, address, room, book_id, id_type, author, year,
                              title, publisher, None, subjects)

        if 'recent' not in session:
            session['recent'] = []
        session['recent'].append(b_id)
        return render_template('form.html', header_name=admin_settings.get_settings().header_name,
                               address=admin_settings.get_settings().default_address)

    # isbn/lccn given
    elif request.method == 'POST' and request.form.get(
            'button_class') == 'auto' or 'isbn' in request.args or 'olid' in request.args:
        if 'isbn' in request.args:
            id_type = 'isbn'
            book_id = request.args['isbn']
        elif 'olid' in request.args:
            id_type = 'olid'
            book_id = request.args['olid']
        else:
            id_type = request.form['id_type']
            book_id = request.form['search_id']
        title, author, publish_date, publisher, subjects = fetch.lookup_book_info(
            book_id, id_type)
        session['autofilled'] = True
        # print(title, author, publish_date, publisher)
        return render_template('form.html', header_name=admin_settings.get_settings().header_name,
                               address=admin_settings.get_settings().default_address, title=title, author=author,
                               book_id=book_id, id_type=id_type, year=publish_date, publisher=publisher,
                               subjects=subjects)

    else:
        return render_template('form.html', header_name=admin_settings.get_settings().header_name,
                               address=admin_settings.get_settings().default_address)


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/view')


@app.route('/about')
def about():
    return render_template('about.html', header_name=admin_settings.get_settings().header_name)


def run_flask(p=5000):
    db.init_db()
    app.run(port=p, host='0.0.0.0', debug=True)


def create_app():
    db.init_db()
    return app


if __name__ == '__main__':
    db.init_db()
    app.run(port=5000, host='0.0.0.0', debug=True)
