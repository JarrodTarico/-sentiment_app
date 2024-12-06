from prometheus_client import Gauge, start_http_server, REGISTRY

try:
    start_http_server(8000)
except Exception as e:
    print(e)

def write_metric(name, val):
    gauge = REGISTRY._names_to_collectors.get(f'sentiment_app_{name}')
    if not gauge:
        gauge = Gauge(f'sentiment_app_{name}', f"{name}")    
        print("ALLCAPS")
    gauge.set(val)
