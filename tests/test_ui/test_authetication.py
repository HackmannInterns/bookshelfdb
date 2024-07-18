import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
from multiprocessing import Process
from app import run_flask
import shutil
from admin import get_settings, update_yaml
from selenium.common.exceptions import NoSuchDriverException


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


def login_wihtout_moving(browser, password):
    pass_input = browser.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(3)


def test_add_perm(flask_init, browser):
    update_yaml(viewer_can_add=False)

    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/add-book")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    assert title_text.text == "You cannot add with your current authentication level; Editor or greater required"

    from app import EDITOR_PASSWORD
    login_wihtout_moving(browser, EDITOR_PASSWORD)
    assert browser.title == "Add Book"


def test_remove_perm(flask_init, browser):
    update_yaml(editor_can_remove=False)

    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/delete?q=-1")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    assert title_text.text == "You cannot remove with your current authentication level; Admin or greater required"

    from app import ADMIN_PASSWORD
    login_wihtout_moving(browser, ADMIN_PASSWORD)
    assert browser.title == "Library"


def test_admin_perm(flask_init, browser):
    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/admin")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    assert title_text.text == "You cannot view admin with your current authentication level; Admin or greater required"

    from app import ADMIN_PASSWORD
    login_wihtout_moving(browser, ADMIN_PASSWORD)
    assert browser.title == "Settings"


def test_edit_perm(flask_init, browser):
    browser.get("http://localhost:5000/logout")
    browser.get("http://localhost:5000/edit?q=-1")
    title_text = browser.find_element(By.XPATH, "/html/body/div/h3")
    assert title_text.text == "You cannot edit with your current authentication level; Editor or greater required"

    from app import EDITOR_PASSWORD
    login_wihtout_moving(browser, EDITOR_PASSWORD)
    assert browser.title == "Library"
