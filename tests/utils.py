import json
import os
from typing import Dict


CURRENT_DIR = os.path.dirname(__file__)
FIXTURES_PATH = os.path.join(CURRENT_DIR, 'fixtures')


def get_fixture(file_name: str) -> Dict:
    with open(os.path.join(FIXTURES_PATH, file_name)) as fp:
        return json.load(fp)


def with_fixture(fixture_path):
    def wrapper(func):
        def decorator(self):
            fixture = get_fixture(fixture_path)
            return func(self, fixture)
        return decorator
    return wrapper
