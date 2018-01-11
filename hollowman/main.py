import newrelic.agent
from hollowman.app import application
from hollowman.conf import NEW_RELIC_LICENSE_KEY, NEW_RELIC_APP_NAME


if __name__ == "__main__":
    if NEW_RELIC_LICENSE_KEY and NEW_RELIC_APP_NAME:
        newrelic.agent.initialize()

    application.run(host="0.0.0.0", port=5000, debug=True)
