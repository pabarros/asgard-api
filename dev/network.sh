
source "dev/vars.sh"

_=$(docker network rm ${NETWORK_NAME})
net_id=$(docker network create --subnet 172.18.0.0/16 ${NETWORK_NAME})
echo "Recreating network=${NETWORK_NAME} id=${net_id:0:8}"
