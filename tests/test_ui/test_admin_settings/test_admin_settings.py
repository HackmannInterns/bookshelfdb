import shutil
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


def test_admin_viewer_checkbox(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get('localhost:5000/admin')
    time.sleep(3)

    viewer_checkbox = browser.find_element(By.ID, "viewer")

    checkbox_state = viewer_checkbox.is_selected()
    viewer_checkbox.click()
    assert checkbox_state != viewer_checkbox.is_selected()
    submit_button = browser.find_element(
        By.XPATH, '//input[@type="submit" and @value="Save Changes"]')
    submit_button.click()
    time.sleep(.5)

    viewer_checkbox = browser.find_element(By.ID, "viewer")
    checkbox_state = viewer_checkbox.is_selected()
    assert checkbox_state == get_settings().viewer_can_add

    # TODO: address box


def test_admin_editor_checkbox(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get('localhost:5000/admin')
    time.sleep(3)

    editor_checkbox = browser.find_element(By.ID, "editor")

    checkbox_state = editor_checkbox.is_selected()
    editor_checkbox.click()
    assert checkbox_state != editor_checkbox.is_selected()
    submit_button = browser.find_element(
        By.XPATH, '//input[@type="submit" and @value="Save Changes"]')
    submit_button.click()
    time.sleep(.5)

    editor_checkbox = browser.find_element(By.ID, "editor")
    checkbox_state = editor_checkbox.is_selected()
    assert editor_checkbox.is_selected() == get_settings().editor_can_remove


def test_admin_address_textbox(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get('localhost:5000/admin')
    time.sleep(3)

    address_box = browser.find_element(By.ID, "address")

    test_string = "Address T"
    address_box.clear()
    address_box.send_keys(test_string)
    address_box.send_keys(Keys.RETURN)
    time.sleep(.1)

    # submit_button = browser.find_element(
    #     By.XPATH, '//input[@type="submit" and @value="Save Changes"]')
    # submit_button.click()
    # time.sleep(.5)

    address_box = browser.find_element(By.ID, "address")

    assert test_string == get_settings().default_address
    value = address_box.get_attribute("value")
    assert test_string == value
    assert value == get_settings().default_address


def test_admin_title_textbox(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get('localhost:5000/admin')
    time.sleep(3)

    title_box = browser.find_element(By.ID, "header_name")
    title = browser.find_element(By.XPATH, "/html/body/header/h1/a")

    test_string = "Big Boy Test Title"
    title_box.clear()
    title_box.send_keys(test_string)
    title_box.send_keys(Keys.RETURN)
    time.sleep(.1)

    # submit_button = browser.find_element(
    #     By.XPATH, '//input[@type="submit" and @value="Save Changes"]')
    # submit_button.click()
    # time.sleep(.5)

    title = browser.find_element(By.XPATH, "/html/body/header/h1/a")
    title_box = browser.find_element(By.ID, "header_name")

    assert title.text == get_settings().header_name
    value = title_box.get_attribute("value")
    assert title.text == value
    assert value == get_settings().header_name
