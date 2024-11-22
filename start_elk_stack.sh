# Creates a network of Docker Containers
docker network create elk


docker run --name elasticsearch --net elk -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.10.2
docker run --name kibana --net elk -p 5601:5601 docker.elastic.co/kibana/kibana:8.10.2
docker run --name logstash --net elk -p 5000:5000 -v "$(pwd)/logstash.conf:/usr/share/logstash/pipeline/logstash.conf" docker.elastic.co/logstash/logstash:8.10.2
