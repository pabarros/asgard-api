import os

os.environ["ENV"] = "TEST"

os.environ["TEST_DB_URL"] = os.getenv(
    "TEST_DB_URL", "postgresql://postgres@172.18.0.41/asgard"
)

os.environ["TEST_STATS_API_URL"] = os.getenv(
    "TEST_STATS_API_URL", "http://172.18.70.1:9200"
)

os.environ["TEST_ASYNCWORKER_HTTP_PORT"] = os.getenv(
    "TEST_ASYNCWORKER_HTTP_PORT", "9999"
)

assert os.environ["ENV"] == "TEST"
