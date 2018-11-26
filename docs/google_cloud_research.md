# Set Up Dev Environment
## Setup the GCloud CLI
```bash
export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install google-cloud-sdk

# Install the python hooks
sudo apt-get install google-cloud-sdk-app-engine-python google-cloud-sdk-app-engine-python-extras

# Install the big table emulator
sudo apt-get install google-cloud-sdk-bigtable-emulator

# Start the google cloud service
gcloud init
```
**Note: The apt-repo may contain some errors. Consider reinstalling from source.**
https://stackoverflow.com/questions/42697026/install-google-cloud-components-error-from-gcloud-command

# Hadoop (Master DB)
https://cloud.google.com/bigtable/docs/creating-hadoop-cluster

Why use Hadoop?
> Hadoop is not a type of database, but rather a software ecosystem that allows for massively parallel computing. It is 
an enabler of certain types NoSQL distributed databases (such as HBase), which can allow for data to be spread across 
thousands of servers with little reduction in performance.

### Setting up the Hadoop/MongoDB Cluster on Google Cloud
**Note: We will not be using the BigTable instance to create the Hadoop cluster as it requires an expensive upkeep 
($1/hr)**
https://cloud.google.com/bigtable/docs/creating-instance 

The cloud service that will be used is the GCloud Dataproc Service. It will run both the Hadoop and Spark clusters:
https://cloud.google.com/dataproc/

Spark Tutorial:
https://cloud.google.com/dataproc/docs/quickstarts/quickstart-console

We are currently using a free trial account and are limited to 12 VCPU's.

Tutorial to set up the Hadoop network on GCloud:
https://medium.com/google-cloud/launch-a-hadoop-cluster-in-90-seconds-or-less-in-google-cloud-dataproc-b3acc1c02598
https://www.youtube.com/watch?v=6DD-vBdJJxk

Installing MongoDB on Hadoop:
https://docs.mongodb.com/ecosystem/tutorial/getting-started-with-hadoop/

At this point it seems to be more programing Google than the actual frameworks...going to switch to Kubernetes