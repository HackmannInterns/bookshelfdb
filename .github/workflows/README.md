# Bookshelfdb Actions
Our CI for the project

## Docker Image CI
View: [create-docker.yml](/create-docker.yml)

This Action will create the docker image and push it to DockerHub, where we keep our images.
Pushes in the dev branch will build and push the image to :dev on DockerHub.
Pushes in the main branch will build and push the image to :latest on DockerHub.
Additionally, new images can be made using workflow_dispatch.

## Python Tests
View: [python-app.yml](/python-app.yml)

This Action is responsible for running tests for the majority of our backend (written in Python's Pytests).
These tests run every time code is pushed to any branch.

Tests include:
- Testing our database
- Testing API connection with the OpenLibrary
- Testing the caching we do for the OpenLibrary API
- Testing parsing for the OpenLibrary API
- Testing the in-app settings

We plan to include more tests as we build out the application.

## Selenium Tests
View: [selenium-tests.yml](/selenium-tests.yml)

This Action will run tests against a GeckoDriver (FireFox) browser.
These tests run only when requested to, as they take forever.
The Action is run using workflow_dispatch.
Before PRing into main, these tests should be run against the dev branch.

Tests include:
- Testing each page loads and works
- Testing admin functionality

We plan to include more tests as we build out the application, especially functionality tests.
