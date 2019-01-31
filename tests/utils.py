import json
import os
from typing import Dict


CURRENT_DIR = os.path.dirname(__file__)
FIXTURES_PATH = os.path.join(CURRENT_DIR, "fixtures")


def get_fixture(file_name: str) -> Dict:
    with open(os.path.join(FIXTURES_PATH, file_name)) as fp:
        return json.load(fp)


def get_raw_fixture(file_name: str) -> Dict:
    with open(os.path.join(FIXTURES_PATH, file_name)) as fp:
        return fp.read()


def with_json_fixture(fixture_path):
    def wrapper(func):
        def decorator(self, *args):
            fixture = get_fixture(fixture_path)
            return func(self, *args, fixture)

        return decorator

    return wrapper
