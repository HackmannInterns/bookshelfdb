import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        # options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
        yield driver
        driver.quit()

def login(browser, password):
    browser.get("localhost:5000/login")
    pass_input = browser.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(3)

def test_add_perm(flask_init, browser):
    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/add-book")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    assert title_text.text == "You cannot add with your current authentication level; Editor or greater required"
    login(browser, "editor")
    assert browser.title == "Add Book"

def test_remove_perm(flask_init, browser):
    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/delete?q=-1")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    if get_settings().editor_can_remove:
        assert title_text.text == "You cannot remove with your current authentication level; Editor or greater required"
    else:
        assert title_text.text == "You cannot remove with your current authentication level; Admin or greater required"
    login(browser, "editor")
    assert browser.title == "Library"


def test_admin_perm(flask_init, browser):
    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/admin")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    assert title_text.text == "You cannot view admin with your current authentication level; Admin or greater required"
    login(browser, "admin")
    assert browser.title == "Settings"

def test_edit_perm(flask_init, browser):
    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/edit?q=-1")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    assert title_text.text == "You cannot edit with your current authentication level; Editor or greater required"
    login(browser, "editor")
    assert browser.title == "Library"

