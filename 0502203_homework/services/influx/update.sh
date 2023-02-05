OUTPUT=$(docker ps --all | grep influxdb |awk '{ print $1 }')
docker rm -f $OUTPUT
docker build -t influxdb .
docker run --name influxdb -p 8086:8086 influxdb
docker ps | grep influxdb
docker exec -ti influxdb bash
