source "dev/vars.sh"


BASEDIR=$(dirname $(readlink --canonicalize ${0}))


echo ""
echo "Creating initial apps...${BASEDIR}"
curl -s -H "Content-type: application/json" -X PUT -d@${BASEDIR}/dev/apps/asgard/redis.json http://${MARATHON_IP}:8080/v2/apps

curl -s -H "Content-type: application/json" -X PUT -d@${BASEDIR}/dev/apps/asgard-dev/mysql.json http://${MARATHON_IP}:8080/v2/apps
curl -s -H "Content-type: application/json" -X PUT -d@${BASEDIR}/dev/apps/asgard-dev/phpmyadmin.json http://${MARATHON_IP}:8080/v2/apps
curl -s -H "Content-type: application/json" -X PUT -d@${BASEDIR}/dev/apps/asgard-dev/wordpress.json http://${MARATHON_IP}:8080/v2/apps
curl -s -H "Content-type: application/json" -X PUT -d@${BASEDIR}/dev/apps/asgard-dev/httpbin.json http://${MARATHON_IP}:8080/v2/apps
