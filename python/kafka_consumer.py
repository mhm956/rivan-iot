"""
This script is executed on the VM #1: Traffic Generator Instance
When a fix-msg is received in the Kafka broker, mark the associated database entry as resolved.
"""
import os

from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import kafka_producer

Base = automap_base()
# Create the engine to the database
engine = create_engine('mysql+mysqldb://demouser:demopassword@127.0.0.1:3306/rivandb')
Base.prepare(engine, reflect=True)
ErrorCodes = kafka_producer.ErrorCodes
session = Session(engine)
session.bind_table(table=ErrorCodes, bind=engine)


def consume_kafka():
    """When a fix message is received, update the database"""
    consumer = KafkaConsumer('rivan-fix-msg', bootstrap_servers=[os.environ.get('KAFKA_SERVER_INTERNAL_IP')])
    for message in consumer:
        print("Updating column {}".format(message.value.decode()))
        session.query(ErrorCodes.id, ErrorCodes.active_state). \
            filter(ErrorCodes.id == int(message.value.decode())). \
            update({"active_state": False})
        session.commit()


if __name__ == '__main__':
    try:
        consume_kafka()
    except KeyboardInterrupt:
        print("\nExiting simulation script...")
        session.close()
        exit(0)
