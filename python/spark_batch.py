import glob
from os import path

from pyspark import SparkContext, SparkConf

import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# Run the following if getting java port error
# export PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH
# export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.4-src.zip:$PYTHONPATH


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


def get_timestamp_from_logfile(log_file):
    return path.basename(log_file).split('log.')[1]


if __name__ == '__main__':
    # Get a list of the current logs
    file_list = glob.glob("/home/taylor/logs/*")
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
                  yaxis=dict(title='Number of Errors Reported', range=[0, 400])))
    fig = dict(data=arch_data, layout=layout)
    py.plot(arch_data, filename='rivan-metric', auto_open=False)
