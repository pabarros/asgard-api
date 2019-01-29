
source "dev/vars.sh"

echo "Removing any old containers..."
docker rm -f $(docker ps -aq -f name=asgard_) 2>/dev/null >/dev/null
docker rm -f $(docker ps -aq -f name=mesos-) 2>/dev/null >/dev/null
