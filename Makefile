SHELL := /bin/bash

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
