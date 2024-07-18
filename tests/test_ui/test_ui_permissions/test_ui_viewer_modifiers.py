import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
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

    while os.path.exists(backup_path):
        time.sleep(1)

    if os.path.exists(data_path):
        os.rename(data_path, backup_path)
    else:
        raise FileNotFoundError(f"{data_path} not found")

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


def test_viewer_recent_can_add(browser, flask_init):
    delete_db()
    init_db()
    update_yaml(viewer_can_add=True)

    browser.get("localhost:5000/")
    browser.get("localhost:5000/add-book?isbn=9781566199094")
    browser.find_element(
        By.XPATH, "/html/body/div/div[1]/form/div[2]/input[1]").click()
    browser.get("localhost:5000/edit?q=1")
    assert browser.title == "Edit Book"
    assert browser.title != "Login Required"

    browser.get("localhost:5000/delete?q=1")

    assert browser.title == "Library"
    assert browser.title != "Login Required"


def test_viewer_cannot_add(browser, flask_init):
    delete_db()
    init_db()
    update_yaml(viewer_can_add=False)

    browser.get("localhost:5000/")
    browser.get("localhost:5000/add-book?isbn=9781566199094")

    assert browser.title == "Login Required"
    assert browser.title != "Add Book"


def test_viewer_recent_cannot_add(browser, flask_init):
    # Little goofy ofc, cause the book needs to be added, then setting changed
    delete_db()
    init_db()
    update_yaml(viewer_can_add=True)

    browser.get("localhost:5000/")
    browser.get("localhost:5000/add-book?isbn=9781566199094")
    browser.find_element(
        By.XPATH, "/html/body/div/div[1]/form/div[2]/input[1]").click()

    update_yaml(viewer_can_add=False)

    browser.get("localhost:5000/")
    browser.get("localhost:5000/add-book?isbn=9781566199094")

    assert browser.title == "Login Required"
    assert browser.title != "Add Book"

    browser.get("localhost:5000/edit?q=1")
    assert browser.title == "Edit Book"
    assert browser.title != "Login Required"

    browser.get("localhost:5000/delete?q=1")

    assert browser.title == "Library"
    assert browser.title != "Login Required"
