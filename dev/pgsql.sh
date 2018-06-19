
source "dev/vars.sh"

#Postgres

echo -n "Postgres (${POSTGRES_IP}) "
docker run -d --rm -it --ip ${POSTGRES_IP} \
  --name asgard_pgsql \
  --net ${NETWORK_NAME} \
  -v ${PWD}/scripts/sql/:/docker-entrypoint-initdb.d/:ro \
  postgres:9.4
