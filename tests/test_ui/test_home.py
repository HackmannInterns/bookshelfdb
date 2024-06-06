import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from flask import Flask
import app


@pytest.fixture(scope="module")
def flask_app():
    # Run the app in a separate thread
    thread = threading.Thread(target=app.app.run, kwargs={
                              "host": "127.0.0.1", "port": 5000})
    thread.start()
    # time.sleep(1)  # Give the server some time to start
    yield app.app

    # Teardown - stop the app after the tests
    thread.join()


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
