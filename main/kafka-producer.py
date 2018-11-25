"""
On a random but consistent basis generate error code warnings. These warnings will:
    1. Be saved on a local database to simulate persistence of a warning.
    2. Be sent to the Kafaka broker (remote-hosted) for further analysis.
"""
import random
import socket
import struct
import subprocess
import sys
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import secrets
from kafka import KafkaProducer

engine = create_engine('sqlite:///rivan.db')
sim_net_list = []


class RivanErrorSim:
    def __init__(self):
        """Run initial scripts"""
        # Create the Kafka producer.
        self.producer = KafkaProducer(bootstrap_servers=[secrets.KAFKA_SERVER_INTERNAL_IP])

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

        if not database_exists(engine.url):
            create_database(engine.url)
            print("Created database ------ {}".format(engine.url))

    def generate_error(self):
        """Using a database of known vulnerabilities, create a fake error for the specific arch"""
        error_description = subprocess.check_output(['searchsploit', self.sim_arch])
        range_max = len(error_description.decode().split('\n'))
        error_description = error_description.decode().split('\n')[random.randint(5, range_max - 10)].replace('  ', '')
        # Check that the returned line is a valid error code
        while any(substring in error_description for substring in ['Shellcode', '-------------']):
            error_description = subprocess.check_output(['searchsploit', self.sim_arch])
            range_max = len(error_description.decode().split('\n'))
            error_description = error_description.decode().split('\n')[random.randint(5, range_max - 10)]. \
                replace('  ', '')
        return error_description

    def log_error(self, error_description):
        """Using the error description, create a database entry for that error"""
        pass

    def send_error_code(self, error_description):
        """Create, log, and send an error report to the Kafka broker"""
        # Send the error code message to the Kafka topic. The default topic is 'rivan-error-msg'
        self.producer.send('rivan-error-msg', error_description.encode())


if __name__ == 'main':
    # Check that the CLI was started with the needed argument
    if len(sys.argv) != 2:
        print("Incorrect number of arguments passed.")
        print("Usage: {} <number of runners> ")
        exit(0)

    # Check that a valid number of workers was requested by the CLI argument
    if sys.argv[1] not in range(1, 10):
        print("Please enter a number of workers between 1 and 10")
        exit(0)

    print("Running {} with {} number of traffic generators...".format(sys.argv[0], sys.argv[1]))

    worker_dict = dict()
    for worker in range(1, sys.argv[1]):
        worker_dict["rivan_producer_{}".format(worker)] = RivanErrorSim()

    try:
        while 1:
            for worker in range(1, sys.argv[1]):
                sleep(random.randint(30, 120))  # Sleep between 30 - 120 seconds
                active_worker = worker_dict["rivan_producer_{}".format(worker)]
                error = active_worker.generate_error()
                active_worker.log_error(error)
                active_worker.send_error_code(error)

    except KeyboardInterrupt:
        print("Exiting the simulation...")
        for worker in range(1, sys.argv[1]):
            worker_dict["rivan_producer_{}".format(worker)]. \
                producer.send('rivan-status-msg', 'Disconnecting device at {}'.format(
                    worker_dict["rivan_producer_{}".format(worker)].sim_net_addr).encode())
        # TODO: Need to destroy database on exit for cleaning up
