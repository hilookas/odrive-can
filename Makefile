.PHONY: install_pkg, clean, container, list, test, uml, serve_docs

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

install_pkg:
	@echo "Installing package..."
	pip install .


test:
	pylint -E src
	mypy src
	coverage run -m pytest && coverage report -m


uml: install_pkg
	# generage uml files
	mkdir -p docs/uml/odrive_can
	pyreverse src/odrive_can -o png -d docs/uml/odrive_can

public: uml
	# build html documentation
	mkdocs build -d public

serve_docs: uml
	# serve html documentation
	mkdocs serve -a 0.0.0.0:8000

venv:
	# create virtual environment
	python3 -m venv venv
	venv/bin/pip install -r docker/requirements.txt
	venv/bin/pip install -e .
