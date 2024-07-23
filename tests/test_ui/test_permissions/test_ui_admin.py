import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
from multiprocessing import Process
from app import run_flask
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
#        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
        yield driver
        driver.quit()


def login(browser, password):
    browser.get("localhost:5000/logout")
    browser.get("localhost:5000/")
    browser.get("localhost:5000/login")
    pass_input = browser.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(1)


def test_admin_can_view(flask_init, browser):
    from app import ADMIN_PASSWORD
    browser.get("localhost:5000/logout")
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/")
    time.sleep(.5)
    assert browser.title == "Library"
    assert browser.title != "Login Required"


def test_admin_can_add(flask_init, browser):
    from app import ADMIN_PASSWORD
    browser.get("localhost:5000/logout")
    time.sleep(.5)
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/add-book")
    time.sleep(.5)
    assert browser.title == "Add Book"
    assert browser.title != "Login Required"


def test_admin_can_edit(flask_init, browser):
    from app import ADMIN_PASSWORD
    browser.get("localhost:5000/logout")
    login(browser, ADMIN_PASSWORD)
    browser.get("http://localhost:5000/edit?q=-1")
    time.sleep(.5)
    assert browser.title == "Library"
    assert browser.title != "Login Required"


def test_admin_can_delete(flask_init, browser):
    from app import ADMIN_PASSWORD
    browser.get("localhost:5000/logout")
    login(browser, ADMIN_PASSWORD)
    browser.get("http://localhost:5000/delete?q=-1")
    time.sleep(.5)
    assert browser.title == "Library"
    assert browser.title != "Login Required"


def test_admin_can_view_admin(flask_init, browser):
    from app import ADMIN_PASSWORD
    browser.get("localhost:5000/logout")
    login(browser, ADMIN_PASSWORD)
    browser.get("http://localhost:5000/admin")
    time.sleep(.5)
    assert browser.title == "Settings"
    assert browser.title != "Login Required"
