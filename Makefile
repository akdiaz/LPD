SHELL := /bin/bash

# Don't run every command in a recipe in a different subshell, so that
# we can activate a virtual env and then run commands inside it.
# https://stackoverflow.com/a/55404948
.ONESHELL:

.PHONY: black

all: test

black:
	black .

test:
	tox
build:
	python3 -m build

clean:
	rm dist/ build/ -rfv

push:
	python3 -m twine upload --skip-existing dist/*

virtualenv:
	virtualenv dev_env
	source dev_env/bin/activate
	pip install -e .
