#!/usr/bin/env bash

# Create a cluster with the following settings
## Name: rivan-master
## Initialization Programs: Drill, Hue, Jupyter, Kafka
## Region: US-CENTRAL 1-A
## Zone: US-CENTRAL 1-A

## Master Node:
### Number: 1
### Type: 2 vCPU Machine
### Disk Size (Storage): 200GB

## Worker Nodes:
### Number: 2
### Type: 1 vCPU Machine
### Disk Size (Storage): 150GB

gcloud dataproc clusters create rivan-master \
--initialization-actions=gs://dataproc-initialization-actions/drill/drill.sh,\
gs://dataproc-initialization-actions/hue/hue.sh,\
gs://dataproc-initialization-actions/jupyter/jupyter.sh,\
gs://dataproc-initialization-actions/zookeeper/zookeeper.sh,\
gs://dataproc-initialization-actions/kafka/kafka.sh \
--num-masters=1 \
--master-boot-disk-size=200 \
--master-machine-type=n1-standard-2 \
--num-workers 2 \
--worker-machine-type n1-standard-1 \
--worker-boot-disk-size 150 \
--zone=us-central1-a \
--region=global