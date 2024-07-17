import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
from multiprocessing import Process
from app import run_flask
from selenium.common.exceptions import NoSuchDriverException, NoSuchElementException
from selenium.webdriver.support.ui import Select
import shutil
from admin import update_yaml
from db import delete_db, init_db, create_book


@pytest.fixture(scope='session')
def flask_init():
    # Move data
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "../../../data")
    backup_path = os.path.join(script_dir, "../../../data-BAK")

    while os.path.exists(backup_path):
        time.sleep(1)

    if os.path.exists(data_path):
        os.rename(data_path, backup_path)

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

    if os.path.exists(backup_path):
        if os.path.exists(data_path):
            shutil.rmtree(data_path)
        os.rename(backup_path, data_path)


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
    browser.get("localhost:5000/")
    browser.get("localhost:5000/login")
    pass_input = browser.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(3)


def test_submit_isbn(browser, flask_init):
    from app import EDITOR_PASSWORD
    login(browser, EDITOR_PASSWORD)
    time.sleep(1)
    browser.get("localhost:5000/add-book")
    id_type = browser.find_element(By.ID, "id_type")
    type_select = Select(id_type)
    type_select.select_by_value("isbn")
    option = type_select.first_selected_option
    assert option.get_attribute("value") == "isbn"
    id_input = browser.find_element(By.NAME, "search_id")
    id_input.send_keys("9781566199094")
    search_button = browser.find_element(By.NAME, "action")
    search_button.click()
    display = browser.execute_script(
        "return document.querySelector('body > div > div.text-container > div').style.display")
    time.sleep(1)
    assert display == 'block'
    cancel_button = browser.find_element(
        By.XPATH, "//button[@onclick='cancel_submit()']")
    cancel_button.click()
    time.sleep(5)


def test_submit_lccn(browser, flask_init):
    from app import EDITOR_PASSWORD
    login(browser, EDITOR_PASSWORD)
    time.sleep(1)
    browser.get("localhost:5000/add-book")
    id_type = browser.find_element(By.ID, "id_type")
    type_select = Select(id_type)
    type_select.select_by_value("lccn")
    option = type_select.first_selected_option
    assert option.get_attribute("value") == "lccn"
    id_input = browser.find_element(By.NAME, "search_id")
    id_input.send_keys("75619195")
    search_button = browser.find_element(By.NAME, "action")
    search_button.click()
    display = browser.execute_script(
        "return document.querySelector('body > div > div.text-container > div').style.display")
    time.sleep(1)
    assert display == 'block'
    cancel_button = browser.find_element(
        By.XPATH, "//button[@onclick='cancel_submit()']")
    cancel_button.click()
    time.sleep(5)


def test_submit_olid(browser, flask_init):
    from app import EDITOR_PASSWORD
    login(browser, EDITOR_PASSWORD)
    time.sleep(1)
    browser.get("localhost:5000/add-book")
    id_type = browser.find_element(By.ID, "id_type")
    type_select = Select(id_type)
    type_select.select_by_value("olid")
    option = type_select.first_selected_option
    assert option.get_attribute("value") == "olid"
    id_input = browser.find_element(By.NAME, "search_id")
    id_input.send_keys("OL47195647M")
    search_button = browser.find_element(By.NAME, "action")
    search_button.click()
    display = browser.execute_script(
        "return document.querySelector('body > div > div.text-container > div').style.display")
    time.sleep(1)
    assert display == 'block'
    cancel_button = browser.find_element(
        By.XPATH, "//button[@onclick='cancel_submit()']")
    cancel_button.click()
    time.sleep(5)


def test_edit_book_for_pk(browser, flask_init):
    bookshelf = "shelf_location"
    address = "address"
    room = "room"
    b_id = "ISBN"
    numbers = "909090909090"
    author = "John Whitney"
    year = 2003
    title = "book title"
    publisher = "John Hackmann"
    subjects = "Biography, Horor"

    delete_db()
    init_db()
    update_yaml(editor_can_remove=False)
    create_book(bookshelf, address, room, numbers, b_id, author,
                year, title, publisher, None, subjects)

    from app import EDITOR_PASSWORD
    login(browser, EDITOR_PASSWORD)
    time.sleep(1)
    browser.get("localhost:5000/library")
    kebab_icon = browser.find_element(By.CLASS_NAME, "kebab-menu-icon")
    kebab_icon.click()
    time.sleep(1)
    edit_button = browser.find_element(
        By.XPATH, "//a[contains(text(), 'Edit')]")
    edit_button.click()
    time.sleep(1)
    current_url = browser.current_url
    assert current_url == "http://localhost:5000/edit?q=1"

    try:
        browser.find_element(By.CLASS_NAME, "search")
        raise AssertionError("Element with class 'search' should not exist")
    except NoSuchElementException:
        pass
    try:
        browser.find_element(By.CLASS_NAME, "mass_search")
        raise AssertionError("Element with class 'mass_search' should not exist")
    except NoSuchElementException:
        pass
