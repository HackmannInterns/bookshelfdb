import pytest
import os
import yaml
import json
import sqlite3
import shelve

from admin import ADMIN_YAML_LOCATION,init_yaml, update_yaml, get_settings, export_to_json, import_from_json, clear_cache_db, delete_main_db
from unittest.mock import MagicMock
import admin
import db
import fetch

fake_db = "data/fake.db"
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

@pytest.fixture
def set_up():
    fetch.CACHE_DB_LOCATION = fake_cache
    db.DB_LOCATION = fake_db
    db.init_db(fake_db)
    init_yaml()
    update_yaml(False,True,"")

@pytest.fixture
def mock_shelve(monkeypatch):
    # Create a mock shelf object
    mock_shelf = MagicMock()
    # Mock the shelve.open method to return the mock shelf
    monkeypatch.setattr(shelve, 'open', MagicMock(return_value=mock_shelf))
    return mock_shelf


def test_init_yaml():
    admin.ADMIN_YAML_LOCATION = yml
    init_yaml()
    print(admin.ADMIN_YAML_LOCATION)
    with open(admin.ADMIN_YAML_LOCATION, 'r') as file:
        data = yaml.safe_load(file)

    assert data['visitor_can_add'] == False
    assert data['editor_can_remove'] == True
    assert data['default_address'] == ""


def test_update_yaml():
    test_visitor = True
    test_editor = False
    test_address = "233 Ember"

    update_yaml(test_visitor,test_editor,test_address)

    with open(admin.ADMIN_YAML_LOCATION, 'r') as file:
        data = yaml.safe_load(file)

    assert data['visitor_can_add'] == test_visitor
    assert data['editor_can_remove'] == test_editor
    assert data['default_address'] == test_address

def test_get_settings():
    update_yaml(False,True,"")
    settings = get_settings()

    assert settings.visitor_can_add == False
    assert settings.editor_can_remove == True
    assert settings.default_address == ""

def test_export_to_json():
    with open(export_to_json(), 'r') as f:
        file_content = f.read()
    data = json.loads(file_content)

    for i in data:
        assert i[1] != None
        assert i[2] != None
        assert i[3] != None
        assert i[4] != None
        assert i[5] != None
        assert i[6] != None
        assert i[7] != None
        assert i[8] != None
        assert i[9] != None
        assert i[11] != None

def test_import_from_json():
    clear_table("books", fake_db)
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

    db.create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, subjects, None, fake_db)

    export_to_json()

    clear_table("books", fake_db)
    db.init_db(fake_db)

    with open(admin.EXPORT_FILE_LOCATION, 'rb') as file_storage:
        import_from_json(file_storage)

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

  

def test_clear_cache_db(mock_shelve):
    key = 'test_key'
    value = 'test_value'
    
    fetch.save_to_cache(key, value)
    
    # Assert that the value was set correctly in the mock shelf
    mock_shelve.__enter__.return_value.__setitem__.assert_called_once_with(key, value)

    clear_cache_db()

    assert os.path.isfile(fake_cache) == False

def test_delete_main_db():
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

    db.create_book(bookshelf, address, room, id, numbers, author, year, title, publisher, subjects, None, fake_db)


    delete_main_db()
    
    con = sqlite3.connect(db.DB_LOCATION)
    cur = con.cursor()
    cur.execute('SELECT * FROM books')
    rows = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    con.close()

    assert len(rows) == 0