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
import shutil
from admin import update_yaml
from db import delete_db, init_db


@pytest.fixture(scope='session')
def flask_init():
    # Move data
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "../../../data")
    backup_path = os.path.join(script_dir, "../../../data-BAK")

    if os.path.exists(backup_path):
        if not os.path.exists(data_path):
            os.rename(backup_path, data_path)

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
        options.add_argument("-headless")
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


def test_editor_recent(browser, flask_init):
    delete_db()
    init_db()
    update_yaml(editor_can_remove=False)

    browser.get("localhost:5000/")
    from app import EDITOR_PASSWORD
    login(browser, EDITOR_PASSWORD)
    browser.get("localhost:5000/add-book?isbn=9781566199094")
    browser.find_element(
        By.XPATH, "/html/body/div/div[1]/form/div[2]/input[1]").click()
    browser.get("localhost:5000/edit?q=1")
    assert browser.title == "Edit Book"
    assert browser.title != "Login Required"

    browser.get("localhost:5000/delete?q=1")

    assert browser.title == "Library"
    assert browser.title != "Login Required"


def test_editor_can_delete(browser, flask_init):
    delete_db()
    init_db()
    update_yaml(editor_can_remove=True)
    browser.get("localhost:5000/")
    from app import EDITOR_PASSWORD
    login(browser, EDITOR_PASSWORD)
    browser.get("localhost:5000/add-book?isbn=9781566199094")
    browser.find_element(
        By.XPATH, "/html/body/div/div[1]/form/div[2]/input[1]").click()

    browser.get("localhost:5000/logout")
    login(browser, EDITOR_PASSWORD)

    browser.get("localhost:5000/delete?q=1")

    assert browser.title == "Library"
    assert browser.title != "Login Required"


def test_editor_recent_can_delete(browser, flask_init):
    delete_db()
    init_db()
    update_yaml(editor_can_remove=True)
    browser.get("localhost:5000/")
    from app import EDITOR_PASSWORD
    login(browser, EDITOR_PASSWORD)
    browser.get("localhost:5000/add-book?isbn=9781566199094")
    browser.find_element(
        By.XPATH, "/html/body/div/div[1]/form/div[2]/input[1]").click()

    browser.get("localhost:5000/delete?q=1")

    assert browser.title == "Library"
    assert browser.title != "Login Required"
