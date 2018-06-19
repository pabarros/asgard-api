
source "dev/vars.sh"

## MESOS
MESOS_QUORUM=1
MESOS_WORK_DIR=/var/lib/mesos
MESOS_HOSTNAME_LOOKUP=false
MESOS_ZK=zk://${ZK_CLUSTER_IPS}/mesos
#  volumes:
#    - /var/lib/mesos/:/var/lib/mesos/:rw

echo -n "Mesos Master (${MESOS_MASTER_1_IP}) "
docker run -d -it --ip ${MESOS_MASTER_1_IP} \
  --name asgard_mesosmaster_1 \
  --net ${NETWORK_NAME} \
  -e MESOS_IP=${MESOS_MASTER_1_IP} \
  --env-file <(
echo MESOS_QUORUM=${MESOS_QUORUM}
echo MESOS_WORK_DIR=${MESOS_WORK_DIR}
echo MESOS_HOSTNAME_LOOKUP=${MESOS_HOSTNAME_LOOKUP}
echo MESOS_ZK=${MESOS_ZK}
) daltonmatos/mesos:0.0.3 /usr/sbin/mesos-master

echo -n "Mesos Master (${MESOS_MASTER_2_IP}) "
docker run -d -it --ip ${MESOS_MASTER_2_IP} \
  --name asgard_mesosmaster_2 \
  --net ${NETWORK_NAME} \
  -e MESOS_IP=${MESOS_MASTER_2_IP} \
  --env-file <(
echo MESOS_QUORUM=${MESOS_QUORUM}
echo MESOS_WORK_DIR=${MESOS_WORK_DIR}
echo MESOS_HOSTNAME_LOOKUP=${MESOS_HOSTNAME_LOOKUP}
echo MESOS_ZK=${MESOS_ZK}
) daltonmatos/mesos:0.0.3 /usr/sbin/mesos-master

echo -n "Mesos Master (${MESOS_MASTER_3_IP}) "
docker run -d -it --ip ${MESOS_MASTER_3_IP} \
  --name asgard_mesosmaster_3 \
  --net ${NETWORK_NAME} \
  -e MESOS_IP=${MESOS_MASTER_3_IP} \
  --env-file <(
echo MESOS_QUORUM=${MESOS_QUORUM}
echo MESOS_WORK_DIR=${MESOS_WORK_DIR}
echo MESOS_HOSTNAME_LOOKUP=${MESOS_HOSTNAME_LOOKUP}
echo MESOS_ZK=${MESOS_ZK}
) daltonmatos/mesos:0.0.3 /usr/sbin/mesos-master

