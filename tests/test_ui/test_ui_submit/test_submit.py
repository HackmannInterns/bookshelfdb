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
from selenium.webdriver.support.ui import Select


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
    browser.get("localhost:5000/")
    browser.get("localhost:5000/login")
    pass_input = browser.find_element(By.NAME, "password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(3)


def test_submit_isbn(browser):
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


def test_submit_lccn(browser):
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


def test_submit_olid(browser):
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
