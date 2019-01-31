import os

TEST_PGSQL_DSN = os.getenv(
    "ASGARD_TEST_PGSQL_DSN", "postgresql://postgres@172.18.0.41/asgard"
)
