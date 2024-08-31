#!/bin/bash

function migrate() {
  docker compose run --rm web python manage.py migrate
}

function createsuperuser() {
  docker compose run --rm web python manage.py createsuperuser
}

"$@"
