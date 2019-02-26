import os

ASGARD_RABBITMQ_HOST = "127.0.0.1"
ASGARD_RABBITMQ_USER = "guest"
ASGARD_RABBITMQ_PASS = "guest"
ASGARD_RABBITMQ_PREFETCH = 32

ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT = int(
    os.getenv("ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT", 1)
)
ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT = int(
    os.getenv("ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT", 30)
)

# Configs que foram migradas do pacote `hollowman.conf`.
# Depois vamos mudar o prefixo de `HOLLOWMAN_` para `ASGARD_`
SECRET_KEY = os.getenv("HOLLOWMAN_SECRET_KEY", "secret")
