import json
import os
from typing import Dict
from tests.conf import TEST_MESOS_ADDRESS


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


def add_agent_running_tasks(rsps, agent_id):
    agent_info = get_fixture(f"agents/{agent_id}/info.json")
    agent_containers = get_fixture(f"agents/{agent_id}/containers.json")
    rsps.get(
        f"http://{agent_info['hostname']}:{agent_info['port']}/containers",
        payload=agent_containers,
        status=200,
    )


def build_mesos_cluster(rsps, *agent_ids):
    all_agents_info = []
    rsps.get(
        f"{TEST_MESOS_ADDRESS}/redirect",
        status=301,
        headers={"Location": TEST_MESOS_ADDRESS},
    )
    for agent_id in agent_ids:
        agent_info = get_fixture(f"agents/{agent_id}/info.json")
        all_agents_info.append(agent_info)
        add_agent_running_tasks(rsps, agent_id)
        rsps.get(
            f"{TEST_MESOS_ADDRESS}/slaves?slave_id={agent_id}",
            payload={"slaves": [agent_info]},
            status=200,
        )

    rsps.get(
        f"{TEST_MESOS_ADDRESS}/slaves", payload={"slaves": all_agents_info}, status=200
    )
