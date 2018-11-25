import secrets
from kafka import KafkaConsumer


consumer = KafkaConsumer('rivan-error-report', bootstrap_servers=[secrets.KAFKA_SERVER_EXTERNAL_IP])
for message in consumer:
    print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                         message.offset, message.key,
                                         message.value))
