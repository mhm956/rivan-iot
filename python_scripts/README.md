Set up of the TrafficProducer VM
On the GCE console:
* Selected the Ubuntu 18.04 image and created instance with 2 vCPUs
* SSH'd into the console from local host
* Installed Docker
* pip install sqlalchemy kafka # TODO: Add pip freeze
* Installed exploitdb https://github.com/offensive-security/exploitdb
* Cloned repo to the home directory
* Ran locally # TODO: Make this a service that starts on boot.


Set up of the Kafka VM
* Setup using a marketplace solution from GCE Deployment Marketplace

Set up of the Apache "Big Top" Hadoop cluster
https://github.com/GoogleCloudPlatform/click-to-deploy/blob/master/k8s/spark-operator/README.md

Set up of the Spark Client VM
* Using a Juju deployment in standalone mode