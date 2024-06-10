import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from flask import Flask
import time
from multiprocessing import Process
from app import run_flask


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


def test_view_page(flask_init, browser):
    browser.get("localhost:5000/view")
    assert browser.title == "Book Table"


def test_scan_page(flask_init, browser):
    browser.get("localhost:5000/scan")
    assert browser.title == "Barcode Scanner"


def test_edit_page(flask_init, browser):
    browser.get("localhost:5000/edit")
    assert browser.title == "Login Required"


def test_delete_page(flask_init, browser):
    browser.get("localhost:5000/delete")
    assert browser.title == "Login Required"

def test_none_page(flask_init, browser):
    browser.get("localhost:5000/jared")
    assert browser.title == "404 Not Found"
