import json
import sys

from marathon.client import MarathonClient
from marathon.models.group import MarathonGroup
from marathon.util import MarathonJsonEncoder

from hollowman.marathon.group import AsgardAppGroup


def _patch_docker_params(params):
    for p in params:
        for k, v in p.items():
            if "=" in v:
                idx_ = v.index("=")
                parts = v.split("=")
                v = parts[0] + "=" + "/sieve" + parts[1]
                p[k] = v


_group = AsgardAppGroup(MarathonGroup.from_json(json.loads(sys.stdin.read())))

for group in _group.iterate_groups():
    group.id = "/sieve{}".format(group.id)
    del group.version
    print(group.id, file=sys.stderr)
    for app in group.apps:
        app.id = "/sieve{}".format(app.id)
        app.fetch = []
        del app.version
        _patch_docker_params(
            [
                p
                for p in app.container.docker.parameters
                if p["value"].startswith("hollowman.appname")
            ]
        )
        print(" >", app.id, app.container.docker.parameters, file=sys.stderr)

print(json.dumps(_group._marathon_group, cls=MarathonJsonEncoder))
