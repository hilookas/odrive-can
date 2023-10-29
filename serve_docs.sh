#!/usr/bin/env bash
export PORT=8001
echo "Serving docs on port http://localhost:$PORT"

docker run --rm -it -p $PORT:8000 -v ${PWD}:/docs sjev/mkdocs
