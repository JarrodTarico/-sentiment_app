from logstash import TCPLogstashHandler
import logging



def get_logger(name):
    logstash_handler = TCPLogstashHandler('192.168.1.166', 5100, version=1)
    logger = logging.getLogger(name)
    logger.addHandler(logstash_handler)
    logger.setLevel(logging.INFO)
    return logger
