"""
This script is executed on the VM #1: Traffic Generator Instance
When a fix-msg is received in the Kafka broker, mark the associated database entry as resolved.
"""
import os

from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

Base = automap_base()
engine = create_engine('sqlite:///rivan.db')  # Create the engine to the database
Base.prepare(engine, reflect=True)
ErrorCodes = Base.classes.error_codes
session = Session(engine)


def consume_kafka():
    """When a fix message is received, update the database"""
    consumer = KafkaConsumer('rivan-fix-msg', bootstrap_servers=[os.environ.get('KAFKA_SERVER_INTERNAL_IP')])
    for message in consumer:
        print("Updating column {}".format(message.value.decode()))
        # session.query(ErrorCodes.id, ErrorCodes.active_state). \
        #     filter(ErrorCodes.id == int(message.value.decode())). \
        #     update({"active_state": False})
        # TODO: Figure out how to deal with the locking sqlite database


if __name__ == '__main__':
    consume_kafka()
