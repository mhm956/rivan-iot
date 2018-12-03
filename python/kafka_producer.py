"""
This script is executed on the VM #1: Traffic Generator Instance
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

from kafka import KafkaProducer
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

sim_net_list = []
engine = create_engine('mysql+mysqldb://demouser:demopassword@127.0.0.1:3306/rivandb')  # Create the engine to the database
Base = declarative_base()
Session = sessionmaker(bind=engine)  # Bind the session to the engine
session = Session()
producer = KafkaProducer(bootstrap_servers=[os.environ.get('KAFKA_SERVER_INTERNAL_IP')])

if not database_exists(engine.url):
    create_database(engine.url)
    print("Created database ------ {}".format(engine.url))


class ErrorCodes(Base):
    __tablename__ = 'error_codes'

    id = Column(Integer, primary_key=True)
    active_state = Column(Boolean, default=True)
    network_addr = Column(String(32))
    error_code = Column(Integer)
    description = Column(String(254))
    created_dts = Column(DateTime, default=datetime.datetime.utcnow)
    sim_arch = Column(String(32))

    def __repr__(self):
        return "<ErrorCodes(network_addr='%s', error_code='%d', description='%s')>" % \
               (self.network_addr, self.error_code, self.description)

    def as_dict(self):
        error_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # error_dict.pop('created_dts')
        error_dict['created_dts'] = str(error_dict['created_dts'])
        return error_dict


def create_table(db_engine):
    """Helper function ot create the table"""
    Base.metadata.create_all(bind=db_engine)


if not engine.dialect.has_table(engine, 'error_codes'):
    create_table(engine)
    print("Created table --------- {}".format('error_codes'))


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

        # Generate a random IP address for the device. If the IP address is duplicated already in database or
        # the IP address is reserved then regenerate the simulated IP address.
        self.sim_net_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        while self.sim_net_addr in ['0.0.0.0', '127.0.0.1', '255.255.255.255'] or \
                self.sim_net_addr in sim_net_list:
            self.sim_net_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        sim_net_list.append(self.sim_net_addr)

        # Select a random architecture
        self.sim_arch = ['Android', 'ARM', 'BSD', 'Linux', 'macOS', 'OSX', 'Windows'][random.randint(0, 6)]
        self.error_percentage = random.randint(1, 30)

    def generate_error(self):
        """Using a database of known vulnerabilities, create a fake error for the specific arch"""
        error_description = None
        if self.error_percentage > random.randint(1, 99):  # If the percentage-based error is greater than the threshold
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

        error_log = ErrorCodes(network_addr=self.sim_net_addr, error_code=self.error_code,
                               description=error_description, sim_arch=self.sim_arch)
        session.add(error_log)
        session.commit()


def send_error_code():
    """Create, log, and send an error report to the Kafka broker"""
    # Send the error code message to the Kafka topic. The default topic is 'rivan-error-msg'
    session.bind_table(table=ErrorCodes, bind=engine)
    query = session.query(ErrorCodes). \
        filter(ErrorCodes.active_state == True)
    for entry in query:
        print("Sending entry #{}: with:\nAddress:\t{}\nArch:\t{}\nError Code:\t{}\nDescription:\t{}\n"
              .format(entry.id, entry.network_addr, entry.sim_arch, entry.error_code, entry.description))
        entry_json = json.dumps(entry.as_dict())  # Turn db object's dictionary into json string
        producer.send('rivan-error-msg', entry_json.encode())


if __name__ == '__main__':
    # Check that the CLI was started with the needed argument
    if len(sys.argv) != 2:
        print("Incorrect number of arguments passed.")
        print("Usage: {} <number of runners> ".format(sys.argv[0]))
        exit(0)

    # Check that a valid number of workers was requested by the CLI argument
    if int(sys.argv[1]) not in range(1, 41):
        print("Please enter a number of workers between 1 and 40")
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
                print("Checking for a new error code for worker on {} (Arch: {} | Error Probability: {}%)"
                      .format(active_worker.sim_net_addr, active_worker.sim_arch, active_worker.error_percentage))
                error = active_worker.generate_error()
                if not error:
                    continue  # If there was no error generated then go on to the next worker
                print("Adding error code for worker on {}".format(active_worker.sim_net_addr))
                active_worker.log_error(error)
            print("Sending error codes to the Kafka server\n")
            send_error_code()
            print("Returning to sleep timer\n")
            sleep(random.randint(5, 30))  # Sleep between 5-30 seconds

    except KeyboardInterrupt:
        print("\n\nExiting the simulation...")
        exit(0)
