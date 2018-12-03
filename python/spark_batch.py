"""
This script is executed on the VM #3: Spark Master/Slave Instance
"""
import glob
from os import path

from pyspark import SparkContext, SparkConf

import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# To run in local mode
conf = SparkConf()
conf.setMaster('local')
conf.setAppName('spark-batch')
sc = SparkContext(conf=conf)


def config_settings():
    plotly.tools.set_credentials_file(username='demouser', api_key='demokey')
    plotly.tools.set_config_file(world_readable=True, sharing='public')


def get_arch_count_from_file(filename, arch):
    rdd = sc.textFile(filename)
    return rdd.filter(lambda s: 'Arch: {}'.format(arch) in s).count()


def get_ext_count_from_file(filename, extention_type):
    rdd = sc.textFile(filename)
    return rdd.filter(lambda s: extention_type in s).count()


def get_timestamp_from_logfile(log_file):
    return path.basename(log_file).split('log.')[1]


if __name__ == '__main__':
    # Get a list of the current logs
    file_list = glob.glob("/home/taylor/logs/*")

    # Create a diagram of the error reports per Architecture
    sim_arch = ['Android', 'ARM', 'BSD', 'Linux', 'macOS', 'OSX', 'Windows']
    arch_data = []
    config_settings()
    for architecture in sim_arch:
        print("Searching log files for {} error types".format(architecture))
        timestamp = []
        arch_count = []
        for file in sorted(file_list):
            if path.basename(file) != 'kafka-spark-log':
                # Generate the two lists for the architecture plot
                timestamp.append(get_timestamp_from_logfile(file))
                arch_count.append(get_arch_count_from_file(file, architecture))
        arch_data.append(go.Scatter(x=timestamp, y=arch_count, mode='lines+markers', name=architecture))
    layout = go.Layout(dict(title='RIVAN Error Reports by Time Metric', xaxis=dict(title='Log File Time'),
                  yaxis=dict(title='Number of Errors Reported', range=[0, 100])))
    fig = dict(data=arch_data, layout=layout)
    py.plot(fig, filename='rivan-metric', auto_open=False)

    # Create a diagram of the error reports per Extention
    extention_list = ['.c', '.cpp', '.rb', '.pl', '.sh', '.py']
    ext_data = []
    for extention in extention_list:
        print("Searching log files for {} extention exploits".format(extention))
        timestamp = []
        ext_count = []
        for file in sorted(file_list):
            if path.basename(file) != 'kafka-spark-log':
                # Generate the two lists for the extension plot
                timestamp.append(get_timestamp_from_logfile(file))
                ext_count.append(get_ext_count_from_file(file, extention))
        ext_data.append(go.Bar(x=timestamp, y=ext_count, name=extention))
    layout = go.Layout(dict(title='RIVAN Error Reports by Exploit Extention', xaxis=dict(title='Log File Time'),
                            yaxis=dict(title='Number of Errors Reported', range=[0, 110]), barmode='stack'))
    fig = dict(data=ext_data, layout=layout)
    py.plot(fig, filename='rivan-extention', auto_open=False)
