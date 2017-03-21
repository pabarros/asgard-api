

import sys
import os
import getpass
from marathon import MarathonClient

marathon_url = sys.argv[1]
user, passw = sys.argv[2], os.getenv("MARATHON_PWD", getpass.getpass())
marathon_client = MarathonClient([marathon_url], username=user, password=passw)

all_apps = marathon_client.list_apps()


print "Total Apps: {}".format(len(all_apps))

for idx, app in enumerate(all_apps):
    if app.constraints:
        has_dc_constraint = any([constraint.field == "workload" for constraint in app.constraints])
        if has_dc_constraint:
            print "app: {}, net={} constraints={}".format(app.id, app.container.docker.network, app.constraints)
    #    marathon_client.update_app(app.id, app)
