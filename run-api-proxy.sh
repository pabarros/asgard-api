#!/usr/bin/env bash

ASGARD_API_PORT=5001
ASGARD_ASYNC_API_PORT=5002

function cleanup() {
  pkill -f -9 hollowman
  pkill -f -9 asgard.api
  exit 0
}


PYTHONPATH=. ASGARD_HTTP_PORT=${ASGARD_API_PORT} pipenv run api &
API_PID=$!

echo "API PID=$API_PID"


ASYNCWORKER_HTTP_PORT=${ASGARD_ASYNC_API_PORT} pipenv run async-api &
ASYNC_API_PID=$!
echo "async API PID=$ASYNC_API_PID"

trap "cleanup $API_PID $ASYNC_API_PID" SIGTERM SIGINT


CONFIG=$(cat <<'HERE'
events {
  worker_connections  4096;
}
http {
  server {
    listen       5000;
    server_name  _;


    location /agents {
      proxy_pass      http://127.0.0.1:5002;
    }

    location /users {
      proxy_pass      http://127.0.0.1:5002;
    }

    location /accounts {
      proxy_pass      http://127.0.0.1:5002;
    }

    location / {
      proxy_pass      http://127.0.0.1:5001;
    }
  }

}
HERE
)

echo $CONFIG > /tmp/asgard-nginx.conf
docker run --net=host -v /tmp/asgard-nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -g 'daemon off;'





read -d r
