
source "dev/vars.sh"

echo "Removing any old containers..."
docker rm -f $(docker ps -aq -f name=asgard_) 2>/dev/null >/dev/null
_=$(docker network rm ${NETWORK_NAME})
net_id=$(docker network create --subnet 172.18.0.0/16 ${NETWORK_NAME})
echo "Recreating network=${NETWORK_NAME} id=${net_id:0:8}"

echo "Sleeping for 3s, ^C to cancel now."
sleep 3
