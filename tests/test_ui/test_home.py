import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from multiprocessing import Process
from app import run_flask
import time
from selenium.common.exceptions import NoSuchDriverException


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


@pytest.fixture(scope="module")
def browser():
    try:
        options = Options()
        options.add_argument("-headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(executable_path="/snap/bin/firefox.geckodriver")
        driver = webdriver.Firefox(options=options, service=service)
        yield driver
        driver.quit()

    except NoSuchDriverException:
        options = Options()
        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
        yield driver
        driver.quit()


def test_app_starts(browser, flask_init):
    browser.get('localhost:5000')
    # We now redirect
    assert browser.title == 'Library'


def test_header_present(browser, flask_init):
    browser.get('localhost:5000')

    header = browser.find_element(By.CLASS_NAME, "header")
    assert header
    header.find_element(By.TAG_NAME, "h1")
    tabs = browser.find_element(By.CLASS_NAME, "tabs")
    assert tabs


def test_input_fields_empty(browser, flask_init):
    # Ensure empty
    browser.get('localhost:5000')
    inputs = browser.find_elements(By.TAG_NAME, "input")
    for i in inputs:
        if i.get_attribute("type") != "submit" and i.get_attribute("type") != "hidden":
            # name = i.get_attribute("class").split(" ")[1]
            assert i.get_attribute("value") == ""


# def test_present_search(browser, flask_init):
#     browser.get('localhost:5000')
#     search_form = browser.find_element(By.CLASS_NAME, "search")
#     assert search_form.value_of_css_property('display') != 'none'
