"""
This script is executed on the VM #3: Spark Master/Slave Instance
"""
import json
import logging
import os
import pathlib
from logging.handlers import TimedRotatingFileHandler
from pprint import pprint

from kafka import KafkaConsumer, KafkaProducer


def consume_kafka_spark():
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    file_path = "/home/taylor/logs/"
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)

    # Rotate the log every 60 minutes
    handler = TimedRotatingFileHandler(file_path + "kafka-spark-log", when="m", interval=5)
    logger.addHandler(handler)

    consumer = KafkaConsumer('rivan-error-msg', bootstrap_servers=[os.environ.get('KAFKA_SERVER_INTERNAL_IP')])
    producer = KafkaProducer(bootstrap_servers=[os.environ.get('KAFKA_SERVER_INTERNAL_IP')])
    for message in consumer:
        json_value = json.loads(message.value.decode())
        pprint(json_value, indent=4)
        logger.info("Level: Info --- DTS: %s --- Device Arch: %s --- Device Address: %s --- Error Code: %s --- Error "
                    "Description: %s" %
                    (json_value.get('created_dts'), json_value.get('sim_arch'), json_value.get('network_addr'), json_value.get('error_code'),
                     json_value.get('description')))
        producer.send('rivan-fix-msg', str(json_value.get("id")).encode())


if __name__ == '__main__':
    try:
        consume_kafka_spark()
    except KeyboardInterrupt:
        print("\nExiting simulation script...")
        exit(0)
