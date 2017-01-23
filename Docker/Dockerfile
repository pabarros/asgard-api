FROM docker.sieve.com.br/alpine/py27/uwsgi20:0.0.10

#Version: 0.0.4

ARG _=""
ENV GIT_COMMIT_HASH=${_}

ENV UWSGI_MODULE=hollowman.app:application
ENV UWSGI_PROCESSES=4

COPY requirements.txt /tmp/
RUN pip --no-cache-dir install -r /tmp/requirements.txt

COPY requirements-dev.txt /tmp/
COPY Docker/test_entrypoint.sh /
RUN chmod a+x /test_entrypoint.sh

COPY . /opt/app
WORKDIR /opt/app
