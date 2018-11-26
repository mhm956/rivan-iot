"""
On a random but consistent basis generate error code warnings. These warnings will:
    1. Be saved on a local database to simulate persistence of a warning.
    2. Be sent to the Kafka broker (remote-hosted) for further analysis.
"""
import os
import random
import socket
import struct
import subprocess
import sys
import datetime
import json
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, functions
from kafka import KafkaProducer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean

sim_net_list = []
engine = create_engine('sqlite:///rivan.db')  # Create the engine to the database
Base = declarative_base()
Session = sessionmaker(bind=engine)  # Bind the session to the engine


class ErrorCodes(Base):
    __tablename__ = 'error_codes'

    id = Column(Integer, primary_key=True)
    active_state = Column(Boolean, default=True)
    network_addr = Column(String)
    error_code = Column(Integer)
    description = Column(String)
    created_dts = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<ErrorCodes(network_addr='%s', error_code='%d', description='%s')>" % \
               (self.network_addr, self.error_code, self.description)


def create_table(db_engine):
    """Helper function ot create the table"""
    Base.metadata.create_all(bind=db_engine)


def serialize_row(row_object):
    """Turn a row from ErrorCodes into a JSON string"""
    temp_log = row_object.__dict__
    temp_log.pop('_sa_instance_state', None)
    temp_log['created_dts'] = str(temp_log['created_dts'])
    return json.dumps(temp_log)


class RivanErrorSim:
    def __init__(self):
        """Run initial scripts"""
        # Initialize the error code
        self.error_code = 0
        # Create the Kafka producer.
        self.producer = KafkaProducer(bootstrap_servers=[os.environ.get('KAFKA_SERVER_INTERNAL_IP')])

        # Generate a random IP address for the device. If the IP address is duplicated already in database or
        # the IP address is reserved then regenerate the simulated IP address.
        self.sim_net_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        while self.sim_net_addr in ['0.0.0.0', '127.0.0.1', '255.255.255.255'] or \
                self.sim_net_addr in sim_net_list:
            self.sim_net_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        sim_net_list.append(self.sim_net_addr)

        # Select a random architecture
        self.sim_arch = ['Android', 'ARM', 'BSD', 'Linux', 'macOS', 'OSX', 'Windows'][random.randint(0, 6)]

        # Publish that a new simulated network is now active.
        self.producer.send('rivan-status-msg', 'Connecting a new {} device from {}'.
                           format(self.sim_arch, self.sim_net_addr).encode())

    def generate_error(self):
        """Using a database of known vulnerabilities, create a fake error for the specific arch"""
        error_description = subprocess.check_output(['searchsploit', self.sim_arch])
        range_max = len(error_description.decode().split('\n'))
        error_description = error_description.decode().split('\n')[random.randint(5, range_max - 10)].replace('  ', '')

        self.error_code = random.randint(1, 10000)  # Generate a new random error code

        # Check that the returned line is a valid error code
        while any(substring in error_description for substring in ['Shellcode', '-------------']):
            error_description = subprocess.check_output(['searchsploit', self.sim_arch])
            range_max = len(error_description.decode().split('\n'))
            error_description = error_description.decode().split('\n')[random.randint(5, range_max - 10)]. \
                replace('  ', '')

        return error_description

    def log_error(self, error_description):
        """Using the error description, create a database entry for that error"""

        if not database_exists(engine.url):
            create_database(engine.url)
            print("Created database ------ {}".format(engine.url))

        if not engine.dialect.has_table(engine, 'error_codes'):
            create_table(engine)
            print("Created table --------- {}".format('error_codes'))

        session = Session()
        error_log = ErrorCodes(network_addr=self.sim_net_addr, error_code=self.error_code,
                               description=error_description)
        print("1: ", error_log)
        session.add(error_log)
        print("2: ", error_log)
        session.commit()
        print("3: ", error_log)
        return serialize_row(error_log)

    def send_error_code(self, error_description):
        """Create, log, and send an error report to the Kafka broker"""
        # Send the error code message to the Kafka topic. The default topic is 'rivan-error-msg'
        self.producer.send('rivan-error-msg', error_description.encode())


if __name__ == '__main__':
    # Check that the CLI was started with the needed argument
    if len(sys.argv) != 2:
        print("Incorrect number of arguments passed.")
        print("Usage: {} <number of runners> ".format(sys.argv[0]))
        exit(0)

    # Check that a valid number of workers was requested by the CLI argument
    if int(sys.argv[1]) not in range(1, 10):
        print("Please enter a number of workers between 1 and 10")
        exit(0)

    print("Running {} with {} traffic generators...".format(sys.argv[0], sys.argv[1]))

    worker_dict = dict()
    for worker in range(0, int(sys.argv[1])):
        worker_dict["rivan_producer_{}".format(worker)] = RivanErrorSim()
        print("Initialized worker with following constrains:\n- Network Address: {}\n- Arch: {}"
              .format(worker_dict["rivan_producer_{}".format(worker)].sim_net_addr,
                      worker_dict["rivan_producer_{}".format(worker)].sim_arch))

    try:
        while 1:
            for worker in range(0, int(sys.argv[1])):
                active_worker = worker_dict["rivan_producer_{}".format(worker)]
                print("Generating new error code for worker on {}".format(active_worker.sim_net_addr))
                error = active_worker.generate_error()
                print("Adding error code for worker on {}".format(active_worker.sim_net_addr))
                error_json = active_worker.log_error(error)
                print("Sending error code to Kafka for worker on {} --> Error Code: {}".
                      format(active_worker.sim_net_addr, active_worker.error_code))
                active_worker.send_error_code(error_json)
                sleep(random.randint(5, 10))  # Sleep between 30 - 120 seconds
            print("Returning to sleep timer")
            sleep(random.randint(5, 30))  # Sleep between 30 - 120 seconds TODO: Up the sleep count

    except KeyboardInterrupt:
        print("\n\nExiting the simulation...")
        for worker in range(0, int(sys.argv[1])):
            worker_dict["rivan_producer_{}".format(worker)]. \
                producer.send('rivan-status-msg', 'Disconnecting device at {}'.format(
                    worker_dict["rivan_producer_{}".format(worker)].sim_net_addr).encode())
