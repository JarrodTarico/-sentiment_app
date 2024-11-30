import schedule, psutil, time

def get_host_metrics():
    metrics = {
        "cpu_utilization": psutil.cpu_percent(interval=1),
        "memory_utilization": psutil.virtual_memory().percent,
        "disk_io_operations": psutil.disk_io_counters().read_count + psutil.disk_io_counters().write_count,
        "timestamp": time.time()
    }
    return metrics

def gather_and_store_metrics():
    metrics = get_host_metrics()
    print(metrics)

schedule.every(15).seconds.do(gather_and_store_metrics)

while True:
    schedule.run_pending()
    time.sleep(1)
