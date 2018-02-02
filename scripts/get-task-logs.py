
import requests
import sys
import os

import ipdb
ipdb.set_trace()
proxies = {
    "http": os.getenv("http_proxy", "")
}

ASGARD_API = os.getenv("ASGARD_API", "http://127.0.0.1:5000")
ASGARD_AUTH = os.getenv("ASGARD_AUTH_HEADER").split(":")[1].strip()

task_id = sys.argv[1]

def get_json(url):
    return requests.get(url, proxies=proxies, headers={"Authorization": f"{ASGARD_AUTH}"}).json()


offset = get_json(f"{ASGARD_API}/tasks/{task_id}/files/read?path=/stderr&offset=-1")['offset']
block_size = 4096
while True:
    url = f"{ASGARD_API}/tasks/{task_id}/files/read?path=/stderr&offset={offset}&length={block_size}"
    content_jon = get_json(url)
    if len(content_jon['data']):
        sys.stdout.write(content_jon['data'])
        offset += len(content_jon['data'])
