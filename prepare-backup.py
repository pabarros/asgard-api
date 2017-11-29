#!/usr/bin/env python

# Script que percorre todas as apps e groups de um json (de Grupo) removendo:
# app.version
# app.fetch
# group.version

import sys
import json

from hollowman.marathon.group import SieveAppGroup
from marathon.models.group import MarathonGroup
from marathon.util import MarathonJsonEncoder


data = open(sys.argv[1]).read()
_g = SieveAppGroup(MarathonGroup.from_json(json.loads(data)))

for group in _g.iterate_groups():
    del group.version
    for app in group.apps:
        del app.version
        del app.fetch

data_output = json.dumps(_g._marathon_group, cls=MarathonJsonEncoder)
print (data_output)
