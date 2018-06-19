
source "dev/vars.sh"

ZOO_SERVERS="server.1=${ZK_1_IP}:2888:3888 server.2=${ZK_2_IP}:2888:3888 server.3=${ZK_3_IP}:2888:3888"
ZOO_PURGE_INTERVAL=10

function zk_node_start() {
    id=${1}
    ip=${2}
    echo -n "ZK (${ip}) "
    docker run -d \
      --name asgard_zk_${id} \
      --rm -it --ip ${ip} \
      -e ZOO_MY_ID=${id} \
      --net ${NETWORK_NAME} \
      --env-file <(
    echo ZOO_SERVERS=${ZOO_SERVERS}
    echo ZOO_PURGE_INTERVAL=${ZOO_PURGE_INTERVAL}
    ) docker.sieve.com.br/infra/zookeeper:0.0.1
}


zk_node_start 1 ${ZK_1_IP}
zk_node_start 2 ${ZK_2_IP}
zk_node_start 3 ${ZK_3_IP}

