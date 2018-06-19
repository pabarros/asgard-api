#!/bin/bash

# Porque não fizemos isso aqui com docker-commpose?
# 1. Existem inúmeras variaveias compartilhadas, por exmeplo, o IP dos ZKs.
# Fazendo isso com compose teríamos que repetir esses valores para todos os compose-files que precisassem deles,
# 2. Existem variáveis compostas por valores de outras variáveis e não podemos fazer essa composição em um envfile; Por isso não usamos envfile.
# 3. Não é possivel passar um envfile pro docker-compose, apenas dentro do compose-file. Se pudéssemos passar até seria pssível
# criar um grande arquivo de env e passar para todas as chamadas do compose.

HERE=$(dirname $(readlink -f $0))

source "dev/vars.sh"
source "dev/network.sh"
source "dev/pgsql.sh"

# ZK Cluster

ZOO_SERVERS="server.1=${ZK_1_IP}:2888:3888 server.2=${ZK_2_IP}:2888:3888 server.3=${ZK_3_IP}:2888:3888"
ZOO_PURGE_INTERVAL=10
echo -n "ZK (${ZK_1_IP}) "
docker run -d \
  --name asgard_zk_1 \
  --rm -it --ip ${ZK_1_IP} \
  -e ZOO_MY_ID=1 \
  --net ${NETWORK_NAME} \
  --env-file <(
echo ZOO_SERVERS=${ZOO_SERVERS}
echo ZOO_PURGE_INTERVAL=${ZOO_PURGE_INTERVAL}
) docker.sieve.com.br/infra/zookeeper:0.0.1

echo -n "ZK (${ZK_2_IP}) "
docker run -d --rm -it --ip ${ZK_2_IP} \
  --name asgard_zk_2 \
  -e ZOO_MY_ID=2 \
  --net ${NETWORK_NAME} \
  --env-file <(
echo ZOO_SERVERS=${ZOO_SERVERS}
echo ZOO_PURGE_INTERVAL=${ZOO_PURGE_INTERVAL}
) docker.sieve.com.br/infra/zookeeper:0.0.1

echo -n "ZK (${ZK_3_IP}) "
docker run -d --rm -it --ip ${ZK_3_IP} \
  --name asgard_zk_3 \
  -e ZOO_MY_ID=3 \
  --net ${NETWORK_NAME} \
  --env-file <(
echo ZOO_SERVERS=${ZOO_SERVERS}
echo ZOO_PURGE_INTERVAL=${ZOO_PURGE_INTERVAL}
) docker.sieve.com.br/infra/zookeeper:0.0.1


source "dev/marathon.sh"
source "dev/mesosmaster.sh"

## MESOS SLAVE
MESOS_ATTRIBUTES=";mesos:slave;workload:general"
MESOS_RESOURCES="cpus(*):4;mem(*):4096;ports(*):[31000-31999];cpus(asgard):1;mem(asgard):1024;ports(asgard):[30000-30999]"
MESOS_MASTER=zk://${ZK_CLUSTER_IPS}/mesos

for SLAVE_IP in `echo ${MESOS_SLAVE_IPS_ACCOUNT_ASGARD_INFRA}`;
do
    echo -n "Mesos Slave (namespace=asgard-infra (${SLAVE_IP}) "
    docker run -d --rm -it --ip ${SLAVE_IP} \
      --name asgard_mesosslave_${RANDOM} \
      --net ${NETWORK_NAME} \
      --env-file <(
    echo MESOS_IP=${SLAVE_IP}
    echo LIBPROCESS_ADVERTISE_IP=${SLAVE_IP}
    echo MESOS_ATTRIBUTES="${MESOS_ATTRIBUTES};owner:asgard-infra"
    echo MESOS_MASTER=${MESOS_MASTER}
    echo MESOS_RESOURCES=${MESOS_RESOURCES}
    ) \
      -v /sys/fs/cgroup:/sys/fs/cgroup \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v $(dirname $(readlink --canonicalize ${0}))/scripts/docker.tar.bz2:/etc/docker.tar.bz2 \
      daltonmatos/mesos:0.0.3
done

for SLAVE_IP in `echo ${MESOS_SLAVE_IPS_ACCOUNT_ASGARD_DEV}`;
do
    echo -n "Mesos Slave (namespace=asgard-dev (${SLAVE_IP}) "
    docker run -d --rm -it --ip ${SLAVE_IP} \
      --name asgard_mesosslave_${RANDOM} \
      --net ${NETWORK_NAME} \
      --env-file <(
    echo MESOS_IP=${SLAVE_IP}
    echo LIBPROCESS_ADVERTISE_IP=${SLAVE_IP}
    echo MESOS_ATTRIBUTES="${MESOS_ATTRIBUTES};owner:asgard-dev"
    echo MESOS_MASTER=${MESOS_MASTER}
    echo MESOS_RESOURCES=${MESOS_RESOURCES}
    ) \
      -v /sys/fs/cgroup:/sys/fs/cgroup \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v $(dirname $(readlink --canonicalize ${0}))/scripts/docker.tar.bz2:/etc/docker.tar.bz2 \
      daltonmatos/mesos:0.0.3
done

#CREATE INITIAL GROUP
echo "Creating initial groups. Waiting for Marathon to come up..."
while true; do
  curl -s -X PUT -d '{"id": "/", "groups": [{"id": "/asgard-dev"}, {"id": "/asgard-infra"}]}' http://${MARATHON_IP}:8080/v2/groups
  if [ $? -eq 0 ]; then
    break;
  fi
done

