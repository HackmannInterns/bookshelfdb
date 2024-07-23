import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from multiprocessing import Process
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
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
    time.sleep(1)


def test_update_elements_page(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/admin")

    versioning = browser.find_element(By.XPATH, "/html/body/div[2]")
    assert versioning
    assert versioning.find_element(By.ID, "current-version")
    assert versioning.find_element(By.ID, "newest-version")
    assert versioning.find_element(By.ID, "refresh-button")
    assert versioning.find_element(By.ID, "update-failed")
    assert versioning.find_element(By.ID, "update-info")


def test_updates_current(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/admin")
    from version import APP_VERSION

    # Current Version
    version = APP_VERSION
    link = 'https://github.com/jellyfin/jellyfin/releases/tag/v10.9.7'

    resp = f"fix_update_info({{newest: '{version}', newest_link: '{link}'}})"
    browser.execute_script(resp)

    versioning = browser.find_element(By.XPATH, "/html/body/div[2]")
    assert versioning.find_element(
        By.ID, "current-version").text == APP_VERSION
    assert versioning.find_element(
        By.ID, "current-version").value_of_css_property('color') == 'rgb(0, 128, 0)'  # Green
    assert versioning.find_element(
        By.ID, "version-link").get_attribute("href") == link
    assert versioning.find_element(
        By.ID, "update-failed").value_of_css_property('display') == "none"
    assert versioning.find_element(
        By.ID, "update-info").value_of_css_property('display') == "none"


def test_updates_newer(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/admin")
    from version import APP_VERSION

    # Current Version
    version = APP_VERSION + '.1'
    link = 'https://github.com/jellyfin/jellyfin/releases/tag/v10.9.8'

    resp = f"fix_update_info({{newest: '{version}', newest_link: '{link}'}})"
    browser.execute_script(resp)

    versioning = browser.find_element(By.XPATH, "/html/body/div[2]")
    assert versioning.find_element(
        By.ID, "current-version").text == APP_VERSION
    assert versioning.find_element(
        By.ID, "version-link").text == version
    assert versioning.find_element(
        By.ID, "current-version").value_of_css_property('color') == 'rgb(255, 0, 0)'  # Red
    assert versioning.find_element(
        By.ID, "version-link").get_attribute("href") == link
    assert versioning.find_element(
        By.ID, "update-failed").value_of_css_property('display') == "none"
    assert versioning.find_element(
        By.ID, "update-info").value_of_css_property('display') == "block"


def test_updates_failed(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/admin")
    from version import APP_VERSION

    # Current Version
    version = 'null'
    link = 'null'

    resp = f"fix_update_info({{newest: {version}, newest_link: {link}}})"
    browser.execute_script(resp)

    versioning = browser.find_element(By.XPATH, "/html/body/div[2]")
    assert versioning.find_element(
        By.ID, "current-version").text == APP_VERSION
    assert versioning.find_element(
        By.ID, "version-link").text == ''
    assert versioning.find_element(
        By.ID, "current-version").value_of_css_property('color') == 'rgb(0, 0, 0)'  # Black
    assert versioning.find_element(
        By.ID, "update-failed").value_of_css_property('display') == "block"
    assert versioning.find_element(
        By.ID, "update-info").value_of_css_property('display') == "none"


def test_updates_spinny(flask_init, browser):
    from app import ADMIN_PASSWORD
    login(browser, ADMIN_PASSWORD)
    browser.get("localhost:5000/admin")

    spinny = browser.find_element(By.ID, "refresh-button")
    spinny.click()

    assert "spinning" in spinny.get_attribute("class")
    time.sleep(5)
    assert "spinning" not in spinny.get_attribute("class")