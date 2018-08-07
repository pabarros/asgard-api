
source "dev/vars.sh"

## MESOS SLAVE
MESOS_ATTRIBUTES=";mesos:slave;workload:general"
MESOS_RESOURCES="cpus(*):4;mem(*):4096;ports(*):[31000-31999];cpus(asgard):1;mem(asgard):1024;ports(asgard):[30000-30999]"
MESOS_MASTER=zk://${ZK_CLUSTER_IPS}/mesos

function start_mesos_slave() {
    id=${RANDOM}
    ip=${1}
    namespace=${2}
    echo -n "Mesos Slave (namespace=${namespace} (${ip}) "
    docker run -d --rm -it --ip ${ip} \
      --name asgard_mesosslave_${RANDOM} \
      --net ${NETWORK_NAME} \
      --env-file <(
    echo MESOS_IP=${ip}
    echo LIBPROCESS_ADVERTISE_IP=${ip}
    echo MESOS_ATTRIBUTES="${MESOS_ATTRIBUTES};owner:${namespace}"
    echo MESOS_MASTER=${MESOS_MASTER}
    echo MESOS_RESOURCES=${MESOS_RESOURCES}
    ) \
      -v /sys/fs/cgroup:/sys/fs/cgroup \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v $(dirname $(readlink --canonicalize ${0}))/../scripts/docker.tar.bz2:/etc/docker.tar.bz2 \
      b2wasgard/mesos:0.0.3
}

start_mesos_slave 172.18.0.51 "asgard-infra"
start_mesos_slave 172.18.0.52 "asgard-infra"
start_mesos_slave 172.18.0.53 "asgard-infra"
start_mesos_slave 172.18.0.54 "asgard-infra"
start_mesos_slave 172.18.0.55 "asgard-infra"
start_mesos_slave 172.18.0.61 "asgard-dev"
start_mesos_slave 172.18.0.62 "asgard-dev"
start_mesos_slave 172.18.0.63 "asgard-dev"
start_mesos_slave 172.18.0.64 "asgard-dev"
start_mesos_slave 172.18.0.65 "asgard-dev"

