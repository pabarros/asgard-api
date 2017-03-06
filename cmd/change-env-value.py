

import sys
import os
import getpass
from marathon import MarathonClient
import json

marathon_url = sys.argv[1]
user, passw = sys.argv[2], os.getenv("MARATHON_PWD")
marathon_client = MarathonClient([marathon_url], username=user, password=passw)

all_apps = marathon_client.list_apps()
bridged_apps = [app for app in all_apps if app.container.docker.network == "BRIDGE"]
hosted_apps = [app for app in all_apps if app.container.docker.network == "HOST"]


print "Total Apps: {}, BRIDGE: {} # HOST:{}".format(len(all_apps), len(bridged_apps), len(hosted_apps))

#import ipdb; ipdb.set_trace()

NEW_REDIS="10.76.98.141"
OLD_REDIS="10.37.58.37"

for idx, app in enumerate(bridged_apps):
#    if idx % 1 == 0:
#        print " Press Key", idx
#        sys.stdin.read(1)

    envs_to_be_migrated = []
    for k, v in app.env.iteritems():
        if 'redis' in k.lower():
            if v == OLD_REDIS:
                envs_to_be_migrated.append(k)
                continue
            if OLD_REDIS in v:
                print " > App {} must also be migrated. {}={}".format(app.id, k, v)
                break

        if 'model_cache_host' in k.lower() and v == OLD_REDIS:
            envs_to_be_migrated.append(k)
            
                
    if envs_to_be_migrated:
        app.fetch = None
        print " > Migrating app {} from redis({}) to redis={}".format(app.id, OLD_REDIS, NEW_REDIS)
        #print "   >", app.env
        print "   > ", ["{}={}".format(env, app.env[env]) for env in envs_to_be_migrated]
        print "   > Press Key to confirm"
        for env in envs_to_be_migrated:
            app.add_env(env, NEW_REDIS)
        #print "   >", app.env
        sys.stdin.read(1)
        #import ipdb; ipdb.set_trace()
        #marathon_client.update_app(app.id, app)
