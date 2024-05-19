# phosphorous-backend

API for phosphorus

## How to install

This project uses Poetry for Python environment management, please install it using pipx according to the [documentation](https://python-poetry.org/docs/#installing-with-pipx)
After that, in a terminal (in the backend directory):

    > poetry install

This will create a Poetry environment and install:

- HTTPX: External API requests
- SQLModel: ORM
- FastAPI: API framework

## How to use

In a terminal (in the backend directory):

    > poetry shell
    > fastapi dev main.py
