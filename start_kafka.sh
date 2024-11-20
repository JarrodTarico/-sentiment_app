#!/bin/bash
cd kafka_2.13-3.9.0

#start zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties    

sleep 5

#start kafka
bin/kafka-server-start.sh config/server.properties  

