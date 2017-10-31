
from hollowman.marathon.group import SieveAppGroup
from marathon.models.group import MarathonGroup
from marathon.client import MarathonClient
from marathon.util import MarathonJsonEncoder

import sys
import json

c = MarathonClient(["http://127.0.0.1:9090"])

group_name = sys.argv[1]

_group = SieveAppGroup(c.get_group(group_name))

for group in _group.iterate_groups():
    group.id = "/sieve{}".format(group.id)
    del group.version
    #print(group.id)
    for app in group.apps:
        app.id = "/sieve{}".format(app.id)
        app.fetch = []
        del app.version
        #print(" >", app.id)

print(json.dumps(_group._marathon_group, cls=MarathonJsonEncoder))


