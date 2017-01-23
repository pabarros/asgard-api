#!/usr/bin/env sh

{
    apk add --update gcc python-dev musl-dev && \
    pip install -r /tmp/requirements-dev.txt && \
    find . -iname *.pyc -delete && \
    py.test --cov=hollowman --cov-report term-missing -v -s
} || {
    exit 1;
}
