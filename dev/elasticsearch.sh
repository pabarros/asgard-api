source "dev/vars.sh"

echo -n "ElasticSearch (${ES_IP}) "
# 172.18.70.1
docker run --rm --net=asgard --ip ${ES_IP} --name "asgard_elasticsearch_$$" -d elasticsearch:5.5-alpine
