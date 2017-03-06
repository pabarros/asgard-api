

import sys
import os
import getpass
from marathon import MarathonClient

marathon_url = sys.argv[1]
user, passw = sys.argv[2], os.getenv("MARATHON_PWD", getpass.getpass())
marathon_client = MarathonClient([marathon_url], username=user, password=passw)

all_apps = marathon_client.list_apps()
bridged_apps = [app for app in all_apps if app.container.docker.network == "BRIDGE"]
hosted_apps = [app for app in all_apps if app.container.docker.network == "HOST"]


print "Total Apps: {}, BRIDGE: {} # HOST:{}".format(len(all_apps), len(bridged_apps), len(hosted_apps))

for idx, app in enumerate(bridged_apps):
    if idx % 10 == 0:
        print " Press Key", idx
        sys.stdin.read(1)
    print " > Updating app: {}".format(app.id)
    app.mem + 1
#    marathon_client.update_app(app.id, app)
