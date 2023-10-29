#!/usr/bin/env bash


docker run --rm -it -p 8000:8000 -v ${PWD}:/docs sjev/mkdocs make serve_docs
