import os

TEST_LOCAL_AIOHTTP_ADDRESS = (
    f"http://127.0.0.1:{os.environ['TEST_ASYNCWORKER_HTTP_PORT']}"
)
