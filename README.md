# Django Poetry Boilerplate

## Description
Use this boilerplate to quickly start a Django project with a PostgreSQL database, poetry and docker setup.
This includes pre-commit hooks for black, flake8 and isort.


## Setup
1. Clone this repository
2. Rename project in `poetry.toml`
3. Run `poetry install --with dev` to install dependencies
4. Run `docker-compose build` to build the docker image
5. Run `docker-compose up -d` to start app and database
6. Run `docker-compose exec app python manage.py migrate` to run migrations
7. Browse to http://localhost:8000 to see the app running

### API docs
Browse to http://127.0.0.1:8000/api/v1/schema/swagger/ to see the API docs.
