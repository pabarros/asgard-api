import os

TEST_MESOS_ADDRESS = "http://10.0.0.1:5050"
TEST_LOCAL_AIOHTTP_ADDRESS = (
    f"http://127.0.0.1:{os.environ['TEST_ASYNCWORKER_HTTP_PORT']}"
)
