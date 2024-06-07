import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from flask import Flask
import db
import time
import requests
from multiprocessing import Process
from app import run_flask


@pytest.fixture(scope="session", autouse=True)
def create_testing_db():
    testing_db = "tmp.db"
    db.init_db(testing_db)
    db.create_book("bookshelf", "address", "room", "book_id", "id_type", "author", "year",
                   "title", "publisher", None, db=testing_db)
    yield db
    # db.delete_db()


@pytest.fixture(scope='session')
def flask_init():
    # Start the Flask app in a separate process
    port = 5000  # Change the port number here if needed
    app_process = Process(target=run_flask, args=(port,))
    app_process.start()

    # Wait for the server to start
    time.sleep(3)

    yield

    # Teardown
    app_process.terminate()
    app_process.join()


@pytest.fixture
def browser():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()


def test_app_starts(browser):
    browser.get('localhost:5000')
    assert browser.title == 'Book Form'


def test_header_present(browser):
    browser.get('localhost:5000')

    header = browser.find_element(By.CLASS_NAME, "header")
    assert header
    header_h1 = header.find_element(By.TAG_NAME, "h1")
    tabs = browser.find_element(By.CLASS_NAME, "tabs")
    assert tabs
    assert header.text == 'Hackmann Library\nSubmit Library Scan'


def test_input_fields_empty(browser):
    # Ensure empty
    browser.get('localhost:5000')
    inputs = browser.find_elements(By.TAG_NAME, "input")
    for i in inputs:
        if i.get_attribute("type") != "submit" and i.get_attribute("type") != "hidden":
            name = i.get_attribute("class").split(" ")[1]
            assert i.get_attribute("value") == ""


def test_present_search(browser):
    browser.get('localhost:5000')
    search_form = browser.find_element(By.CLASS_NAME, "search")
    assert search_form.value_of_css_property('display') != 'none'


def test_not_present_search(browser):
    browser.get('localhost:5000/?edit=1')
    search_form = browser.find_element(By.CLASS_NAME, "search")
    # a = search_form.value_of_css_property('display')
    assert search_form.value_of_css_property('display') == 'none'


def test_not_present_search(browser):
    browser.get('localhost:5000/?edit=1')
    search_form = browser.find_element(By.CLASS_NAME, "search")
    # a = search_form.value_of_css_property('display')
    assert search_form.value_of_css_property('display') == 'none'
