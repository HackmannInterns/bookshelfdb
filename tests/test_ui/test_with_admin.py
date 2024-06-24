import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from multiprocessing import Process
from app import run_flask
from admin import get_settings


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


def login(browser, password):
    browser.get("localhost:5000/login")
    pass_input = browser.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(3)


def test_view_page(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/admin")
    assert browser.title == "Admin Page"


def test_admin_settings(browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get('localhost:5000/admin')
    time.sleep(2)
    editor_checkbox = browser.find_element(By.ID, "editor")
    viewer_checkbox = browser.find_element(By.ID, "viewer")
    assert editor_checkbox.is_selected() == get_settings().editor_can_remove
    assert viewer_checkbox.is_selected() == get_settings().visitor_can_add
    address_box = browser.find_element(By.ID, "address")
    header_box = browser.find_element(By.ID, "header_name")
    assert address_box.get_attribute('value') == get_settings().default_address
    assert header_box.get_attribute('value') == get_settings().header_name


# Requires an entry, not sure how we wanna handle this
# def test_edit_page_with_admin(flask_init, browser):
#     from app import ADMIN_PASSWORD
#     login(browser, ADMIN_PASSWORD)
#     browser.get("localhost:5000/edit?q=1")
#     assert browser.title == "Book Table"


def test_delete_page_with_admin(flask_init, browser):
    from app import ADMIN_PASSWORD
    # Redirects regardless of ability to delete (in this case, we don't ever have a -1)
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/")
    browser.get("localhost:5000/delete?q=-1")
    assert browser.title == "Book Table"
