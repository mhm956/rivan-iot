import json
import logging
import os
import pathlib
from logging.handlers import TimedRotatingFileHandler
from pprint import pprint

from kafka import KafkaConsumer


def consume_kafka_spark():
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    file_path = "/home/taylor/logs/"
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)

    # Rotate the log every 60 minutes
    handler = TimedRotatingFileHandler(file_path + "kafka-spark-log", when="m", interval=60)
    logger.addHandler(handler)

    consumer = KafkaConsumer('rivan-error-msg', bootstrap_servers=[os.environ.get('KAFKA_SERVER_INTERNAL_IP')])
    for message in consumer:
        # TODO: Remove the color codes
        json_value = json.loads(message.value.decode())
        pprint(json_value, indent=4)
        logger.info("Level: Info --- DTS: %s --- Device Address: %s --- Error Code: %s --- Error Description: %s" %
                    (json_value.get('created_dts'), json_value.get('network_addr'), json_value.get('error_code'),
                     json_value.get('description')))


if __name__ == '__main__':
    consume_kafka_spark()
