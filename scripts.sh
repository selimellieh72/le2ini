#!/bin/bash

function makeMigrations() {
  docker compose run --rm web python manage.py makemigrations
}

function migrate() {
  docker compose run --rm web python manage.py migrate
}

function createsuperuser() {
  docker compose run --rm web python manage.py createsuperuser
}

function seed() {
  docker compose run --rm web python manage.py seed_interests && docker compose run --rm web python manage.py seed_cities && docker compose run --rm web python manage.py seed_avatars
}

function collectStatic() {
  docker compose run --rm web python manage.py collectstatic --noinput 
}

"$@"
