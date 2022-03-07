SHELL := /bin/bash

.PHONY: black

all: black

black:
	black .
