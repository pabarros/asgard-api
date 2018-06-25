
source "dev/vars.sh"

echo "Removing any old containers..."
docker rm -f $(docker ps -aq -f name=asgard_)
echo "Recreating network=${NETWORK_NAME}"
docker network rm ${NETWORK_NAME}
docker network create --subnet 172.18.0.0/16 ${NETWORK_NAME}
sleep 2
