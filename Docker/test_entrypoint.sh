#!/bin/env sh

{
    apk add --update gcc python-dev musl-dev && \
    pip install -r requirements-dev.txt && \
    find . -iname *.pyc -delete && \
    py.test --cov=hollowman --cov-report term-missing -v -s
} || {
    return 1;
}
