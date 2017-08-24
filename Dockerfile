FROM docker.sieve.com.br/alpine/py27/uwsgi20:0.0.12

#Version: 0.0.27
#Tag: infra/hollowman

ARG _=""
ENV GIT_COMMIT_HASH=${_}

ENV UWSGI_MODULE=hollowman.app:application
ENV UWSGI_PROCESSES=4

COPY requirements.txt /tmp/
RUN apk -U add libpq \
&& apk add --virtual .deps postgresql-dev gcc g++ make python-dev \
&& pip --no-cache-dir install -r /tmp/requirements.txt \
&& apk del --purge .deps

COPY . /opt/app
WORKDIR /opt/app
