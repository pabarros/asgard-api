import os

os.environ["ENV"] = "TEST_"

os.environ["TEST_DB_URL"] = os.getenv(
    "TEST_DB_URL", "postgresql://postgres@172.18.0.41/asgard"
)

assert os.environ["ENV"] == "TEST_"
