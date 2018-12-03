import glob
import os
from datetime import datetime
from os import path

from pyspark import SparkContext, SparkConf


# To run in paralleled standalone mode
# conf = SparkConf()
# conf.setMaster('spark://10.128.0.4:7077')
# conf.setAppName('spark-batch')
# sc = SparkContext(conf=conf)

# To run in local mode
conf = SparkConf()
conf.setMaster('local')
conf.setAppName('spark-batch')
sc = SparkContext(conf=conf)

rdd = sc.textFile("file:///home/taylor/logs/kafka-spark-log")
rdd.collect()
rdd.first()
rdd.take(5)
rdd.count()


def get_arch_count_from_file(file, timestamp):
    sim_arch = ['Android', 'ARM', 'BSD', 'Linux', 'macOS', 'OSX', 'Windows']
    arch_count = dict()
    rdd = sc.textFile(file)
    for arch in sim_arch:
        arch_count[arch] = rdd.filter(lambda s: 'Arch: {}'.format(arch) in s).count()
        print(arch, arch_count[arch])
    arch_count['timestamp'] = timestamp
    return arch_count


def get_timestamp_from_logfile(log_file):
    return path.basename(log_file).split('log.')[1]


if __name__ == '__main__':
    # Get a list of the current logs
    file_list = glob.glob("/home/taylor/logs/*")
    error_list = []
    for file in file_list:
        if path.basename(file) != 'kafka-spark-log':
            print("Grabbing error data from {}".format(file))
            timestamp = get_timestamp_from_logfile(file)
            arch_count = get_arch_count_from_file(file, timestamp)
            error_list.append(arch_count)