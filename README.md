# Lending System

## Setup
1. Clone this repository.
2. Rename project in `poetry.toml`.
3. Run `poetry install --with dev` to install dependencies.
4. Run `docker-compose build` to build the docker image.
5. Run `docker-compose up -d` to start app and database.
6. Run `docker-compose exec app python manage.py migrate` to run migrations.
7. Browse to http://localhost:8000 to see the app running.
8. Run `docker-compose exec app python manage.py createsuperuser` to create user admin account.