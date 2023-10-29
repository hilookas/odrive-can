.PHONY: install-dev, clean, container, list, test, uml

SHELL := /bin/bash

UID := $(shell id -u)
GID := $(shell id -g)
USERNAME := $(shell id -u -n)

MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MKFILE_DIR := $(dir $(MKFILE_PATH))

list:
	@cat Makefile

clean:
	rm -rf src/*.egg-info dist venv public public docs/uml
	docker container prune -f


test:
	pylint -E src
	mypy src
	coverage run -m pytest && coverage report -m


uml:
	# generage uml files
	mkdir -p docs/uml/odrive_can
	pyreverse src/odrive_can -o png -d docs/uml/odrive_can

public: uml
	# build html documentation
	mkdocs build -d public

