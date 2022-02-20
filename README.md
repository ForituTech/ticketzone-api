## Setting-Up the system
The core dependencies are `poetry` and `python`. You need them installed before
running/ testing the system.

After that you need to run the following to setup:
    - `poetry shell` to create and switch to the venv
    - `poetry install` to install the dependencies
    - `python manage.py migrate` to upgrade the DB state

## Running and testing
To test the system:
    `python manage.py test`
To run the system:
    `python manage.py runserver`