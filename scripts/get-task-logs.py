#!/usr/bin/env python
import requests
import sys
import os



"""
 Como usar:
     ASGARD_AUTH_HEADER="Token <seu-token>" ASGARD_API=https://api-asgard.sieve.com.br ASGARD_ACCOUNT_ID=<account-id> python scripts/get-task-logs.py <task-id>
"""

proxies = {
    "http": os.getenv("http_proxy", "")
}

ASGARD_ACCOUNT_ID = os.getenv("ASGARD_ACCOUNT_ID", "")
ASGARD_API = os.getenv("ASGARD_API", "http://127.0.0.1:5000")
ASGARD_AUTH = os.getenv("ASGARD_AUTH_HEADER").split(":")[1].strip()

task_id = sys.argv[1]
filelog = "/stdout" if len(sys.argv) < 3 else sys.argv[2]

def get_json(url):
    return requests.get(url, proxies=proxies, headers={"Authorization": f"{ASGARD_AUTH}"}).json()


offset = get_json(f"{ASGARD_API}/tasks/{task_id}/files/read?path={filelog}&offset=-1&account_id={ASGARD_ACCOUNT_ID}")['offset'] 
offset -= min(512, offset)
block_size = 4096
while True:
    url = f"{ASGARD_API}/tasks/{task_id}/files/read?path={filelog}&offset={offset}&length={block_size}&account_id={ASGARD_ACCOUNT_ID}"
    content_jon = get_json(url)
    if len(content_jon['data']):
        sys.stdout.write(content_jon['data'])
        offset += len(content_jon['data'])
