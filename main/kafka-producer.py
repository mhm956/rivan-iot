"""
On a random but consistent basis generate error code warnings. These warnings will:
    1. Be saved on a local database to simulate persistence of a warning.
    2. Be sent to the Kafaka broker (remote-hosted) for further analysis.
"""
import random
import socket
import struct
from time import sleep

import secrets
from kafka import KafkaProducer


class RivanErrorSim:
    def __init__(self):
        # Create the Kafka producer.
        self.producer = KafkaProducer(bootstrap_servers=[secrets.KAFKA_SERVER_INTERNAL_IP])

        # Generate a random IP address for the device. If the IP address is duplicated already in database or
        # the IP address is reserved then regenerate the simulated IP address.
        # TODO: Need to make sure that the IP address is not duplicated in the scenario
        self.sim_net_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        while self.sim_net_addr in ['0.0.0.0', '127.0.0.1', '255.255.255.255']:
            self.sim_net_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

        # Publish that a new simulated network is now active.
        self.producer.send('rivan-status-msg', 'Connecting a new device from {}'.format(self.sim_net_addr).encode())

    def generate_error_code(self):
        pass

    def send_error_code(self):
        # Send the error code message to the Kafka topic. The default topic is 'rivan-error-msg'
        self.producer.send('rivan-error-msg', b'dict_values_here')


if __name__ == 'main':
    rivan_producer = RivanErrorSim()
    try:
        while 1:
            sleep(1)
    except KeyboardInterrupt:
        print("Exiting the simulation...")
        rivan_producer.producer.send('rivan-status-msg',
                                     'Disconnecting device at {}'.format(rivan_producer.sim_net_addr).encode())
