from prometheus_client import Gauge, start_http_server
import schedule, psutil, time

cpu_gauge = Gauge('sentiment_app_cpu_usage', 'CPU usage percentage')
memory_gauge = Gauge('sentiment_app_memory_usage', 'Memory usage percentage')
disk_io_operations = Gauge('sentiment_app_disk_io_operations', 'Disk I/O operations')

start_http_server(8000)

def get_host_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_gauge.set(cpu_percent)

    memory_percent = psutil.virtual_memory().percent
    
    memory_gauge.set(memory_percent)

    disk_io = psutil.disk_io_counters().read_count + psutil.disk_io_counters().write_count
    disk_io_operations.set(disk_io)


schedule.every(1).seconds.do(get_host_metrics)

while True:
    schedule.run_pending()
    time.sleep(1)
