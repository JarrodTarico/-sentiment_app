from confluent_kafka import Consumer, TopicPartition, Producer
import schedule, time
import data_ingestion.utils.write_metric_to_prom as prom_writer

consumer_client = Consumer({
    'bootstrap.servers':'localhost:9092',
    'group.id':'dummy-consumer-1',
    'auto.offset.reset':'earliest'
})



tp = TopicPartition('dummy-topic', 0)
consumer_client.assign([tp])

# cpu_gauge = Gauge('sentiment_app_cpu_usage', 'CPU usage percentage')
# memory_gauge = Gauge('sentiment_app_memory_usage', 'Memory usage percentage')
# disk_io_operations = Gauge('sentiment_app_disk_io_operations', 'Disk I/O operations')
# start_http_server(8000)



class ComputeKafkaMetrics:
    '''
        Description: Metrics computation library used to compute kafka metrics at a point in time
        Metrics:
            Produce Count: Total messages produced per topic/partition.
            Consume Count: Total messages consumed per topic/partition.
            Consumer Lag: Difference between the latest produced offset and the last consumed offset.
            Disk Usage: Space used by the topic/partition.
        Collection Frequency:
            Defaults: 
                Times-Series Store (Prometheus): Every 15 Seconds
                Persistent Store (Cassandra): Every 5 Minutes
    '''
    def _compute_producer_offset(self):
        producer_offset = consumer_client.get_watermark_offsets(tp)[1]  
        return producer_offset

    def _compute_consumer_offset(self):
        consumer_offset = consumer_client.committed([tp])[0].offset
        return consumer_offset

    def _compute_consumer_lag(self):
        return self._compute_producer_offset() - self._compute_consumer_offset()
    
    def _compute_disk_usage(self):
        # Number of messages * times the size of one message (1KB)
        total_disk_usage_bytes = self._compute_producer_offset() * 1024
        return total_disk_usage_bytes   
    
    def compute_kafka_metrics(self):
        metrics = []
        metrics.append(('producer_offset', self._compute_producer_offset()))
        metrics.append(('consumer_offset', self._compute_consumer_offset()))
        metrics.append(('consumer_lag', self._compute_consumer_lag()))
        metrics.append(('disk_usage', self._compute_disk_usage()))
        for metric in metrics:
            print(metric[0], metric[1])
            prom_writer.write_metric(metric[0], metric[1])

def run():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    metrics_obj = ComputeKafkaMetrics()
    schedule.every(5).seconds.do(metrics_obj.compute_kafka_metrics)
    run()
    


