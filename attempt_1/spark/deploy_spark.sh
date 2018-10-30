#!/usr/bin/env bash
kubectl create -f master/sparkmaster.yaml

## The following lines are setting a context that loses connection to the Hadoop cluster
#kubectl config set-context spark --namespace=spark-cluster
#kubectl config use-context spark

# Create the spark clusters
kubectl create -f worker/sparkworker.yaml