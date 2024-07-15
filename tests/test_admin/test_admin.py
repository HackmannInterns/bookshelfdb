import pytest
import os
import yaml
import json
import sqlite3
import shelve

from admin import init_yaml, update_yaml, get_settings, export_to_json, import_from_json, clear_cache_db, delete_main_db
import admin
import db
import fetch

fake_db = "data/fakeadmin.db"
yml = "data/dummy.yml"
fake_cache = "data/fake_cache.db"


def clear_table(table_name, db):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Construct the SQL DELETE statement without a condition
    sql_statement = f"DELETE FROM {table_name};"

    # Execute the SQL statement to delete all rows from the table
    cursor.execute(sql_statement)

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()


def clear_data():
    os.remove(yml)
    os.remove(fake_db)
    clear_cache_db(fake_cache)


def set_up():
    admin.ADMIN_YAML_LOCATION = yml
    fetch.CACHE_DB_LOCATION = fake_cache
    db.DB_LOCATION = fake_db
    db.init_db(fake_db)
    shelve.open(fake_cache)
    init_yaml()
    update_yaml(False, True, "", "My Library")


def test_init_yaml():
    set_up()
    admin.ADMIN_YAML_LOCATION = yml
    init_yaml()
    # print(admin.ADMIN_YAML_LOCATION)
    with open(admin.ADMIN_YAML_LOCATION, 'r') as file:
        data = yaml.safe_load(file)

    assert data['visitor_can_add'] is False
    assert data['editor_can_remove'] is True
    assert data['default_address'] == ""
    assert data['header_name'] == "My Library"

    clear_data()


def test_update_yaml():
    set_up()
    test_visitor = True
    test_editor = False
    test_address = "233 Ember"
    test_title = "Not my library"

    update_yaml(test_visitor, test_editor, test_address, test_title)

    with open(admin.ADMIN_YAML_LOCATION, 'r') as file:
        data = yaml.safe_load(file)

    assert data['visitor_can_add'] == test_visitor
    assert data['editor_can_remove'] == test_editor
    assert data['default_address'] == test_address
    assert data['header_name'] == test_title

    clear_data()


def test_get_settings():
    set_up()
    update_yaml(False, True, "")
    settings = get_settings()

    assert settings.visitor_can_add is False
    assert settings.editor_can_remove is True
    assert settings.default_address == ""
    assert settings.header_name == "My Library"

    clear_data()


def test_export_to_json():
    set_up()
    with open(export_to_json(fake_db), 'r') as f:
        file_content = f.read()
    data = json.loads(file_content)

    assert data == []

    clear_data()


def test_import_from_json():
    set_up()
    db.init_db(fake_db)

    bookshelf = "shelf_location"
    address = "address"
    room = "room"
    id = "ISBN"
    numbers = "909090909090"
    author = "John Whitney"
    year = 2003
    title = "book title"
    publisher = "John Hackmann"
    subjects = "Biography, Horor"

    db.create_book(bookshelf, address, room, id, numbers, author,
                   year, title, publisher, None, subjects, fake_db)

    export_to_json(fake_db)

    clear_table("books", fake_db)
    db.init_db(fake_db)

    with open(admin.EXPORT_FILE_LOCATION, 'rb') as file_storage:
        import_from_json(file_storage, fake_db)

    rows = db.read_books(fake_db)
    books = [dict(b_id=row[0],
                  bookshelf_location=row[1],
                  address=row[2],
                  room=row[3],
                  identifier=row[4],
                  identifier_type=row[5],
                  author=row[6],
                  year=row[7],
                  title=row[8],
                  publisher=row[9],
                  description=row[10],
                  subjects=row[11], ) for row in rows]

    for book in books:
        assert bookshelf == book['bookshelf_location']
        assert address == book['address']
        assert room == book['room']
        assert numbers == book['identifier_type']
        assert id == book['identifier']
        assert author == book['author']
        assert year == book['year']
        assert title == book['title']
        assert publisher == book['publisher']
        assert subjects == book['subjects']
        assert book['description'] is None

    clear_data()


def test_clear_cache_db():
    set_up()
    
    fetch.save_to_cache("test_key","test_value")

    assert os.path.exists(fake_cache) or os.path.exists(fake_cache + ".bak") and os.path.exists(fake_cache + ".dat") and os.path.exists(fake_cache + ".dir")


    clear_cache_db(fake_cache)

    assert not os.path.exists(fake_cache)
    assert not os.path.exists(fake_cache + ".bak") and not os.path.exists(fake_cache + ".dat") and not os.path.exists(fake_cache + ".dir")


def test_delete_main_db():
    set_up()
    bookshelf = "shelf_location"
    address = "address"
    room = "room"
    id = "ISBN"
    numbers = "909090909090"
    author = "John Whitney"
    year = 2003
    title = "book title"
    publisher = "John Hackmann"
    subjects = "Biography, Horor"

    db.create_book(bookshelf, address, room, id, numbers, author,
                   year, title, publisher, subjects, None, db=fake_db)

    delete_main_db(db_to_kill=fake_db)

    con = sqlite3.connect(fake_db)
    cur = con.cursor()
    cur.execute('SELECT * FROM books')
    rows = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    con.close()

    assert len(rows) == 0

    clear_data()
