import pytest
from selenium import webdriver
import time
from multiprocessing import Process
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from app import run_flask


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
    options = Options()
    options.add_argument("-headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(executable_path="/snap/bin/firefox.geckodriver")
    driver = webdriver.Firefox(options=options, service=service)
    yield driver
    driver.quit()


def test_library_page(flask_init, browser):
    browser.get("localhost:5000/library")
    assert browser.title == "Book Table"


def test_scan_page(flask_init, browser):
    browser.get("localhost:5000/scan")
    assert browser.title == "Barcode Scanner"


def test_edit_page(flask_init, browser):
    browser.get("localhost:5000/edit?q=1")
    assert browser.title == "Login Required"


def test_delete_page(flask_init, browser):
    browser.get("localhost:5000/delete?q=1")
    assert browser.title == "Login Required"


def test_none_page(flask_init, browser):
    browser.get("localhost:5000/jared")
    assert browser.title == "404 Not Found"


def test_recent_page(flask_init, browser):
    browser.get("localhost:5000/library-recent")
    assert browser.title == "Book Table"
