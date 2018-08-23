source "dev/vars.sh"


BASEDIR=$(dirname $(readlink --canonicalize ${0}))


function put_json(){
  json=${1}
  deployment=$(curl -s -H "Content-type: application/json" -X PUT -d@${json} http://${MARATHON_IP}:8080/v2/apps)
  echo "${json} ${deployment}"
}

echo ""
echo "Creating initial apps...${BASEDIR}"
put_json "${BASEDIR}/dev/apps/asgard/redis.json"

# MySQL 172.18.70.10
put_json "${BASEDIR}/dev/apps/asgard-dev/mysql.json"
put_json "${BASEDIR}/dev/apps/asgard-dev/phpmyadmin.json"
put_json "${BASEDIR}/dev/apps/asgard-dev/wordpress.json"
put_json "${BASEDIR}/dev/apps/asgard-dev/httpbin.json"

# 172.18.80.1
put_json "${BASEDIR}/dev/apps/asgard/rabbitmq.json"

# 172.18.70.1
docker run --rm --net=asgard --ip 172.18.70.1 --name "asgard_elasticsearch_$$" -d elasticsearch:5.5-alpine

# 172.18.70.2
put_json "${BASEDIR}/dev/apps/asgard/fluentd.json"

put_json "${BASEDIR}/dev/apps/asgard/log-indexer.json"
put_json "${BASEDIR}/dev/apps/asgard/kibana.json"
put_json "${BASEDIR}/dev/apps/asgard/stats-collector.json"

put_json "${BASEDIR}/dev/apps/asgard-dev/echo.json"
