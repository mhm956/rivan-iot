#!/usr/bin/env bash

# Creating a kubectl cluster for hadoop
gcloud container clusters create hadoop-cluster
gcloud container clusters get-credentials hadoop-cluster

kubectl create -f ./name_node/namenode.yaml
kubectl create -f ./data_node/datanode.yaml

## Setup a port forward to this box so that you (the admin) can see it is working
# kubectl port-forward dhfs-namenode-0 50070:50070
## Go to https://localhost:50070/dfshealth.html#tab-datanode

## To connect to the hadoop namenode console via ssh
# kubectl exec -ti hdfs-namenode-0 /bin/bash