import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
from multiprocessing import Process
from app import run_flask
from admin import get_settings
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


def test_viewer_can_view(flask_init, browser):
    browser.get("localhost:5000/")
    assert browser.title != "Login Required"


def test_viewer_can_add(flask_init, browser):
    browser.get("localhost:5000/add-book")
    if get_settings().viewer_can_add:
        assert browser.title != "Login Required"
    else:
        assert browser.title == "Login Required"


def test_viewer_can_edit(flask_init, browser):
    browser.get("http://localhost:5000/edit?q=-1")
    assert browser.title == "Login Required"


def test_viewer_can_delete(flask_init, browser):
    browser.get("http://localhost:5000/delete?q=-1")
    assert browser.title == "Login Required"


def test_viewer_can_view_admin(flask_init, browser):
    browser.get("http://localhost:5000/admin")
    assert browser.title == "Login Required"
