## RIVAN (Remote IoT Vulnerability Alert Network)

The goal of the RIVAN network is to provide administrators and developers of distributed IoT systems a system of tools
remotely monitor the current vulnerabilities found in their network. The RIVAN system consists of multiple simulated 
networks which simulate possible real-world vulnerability logs. These logs are collected into a centralized platform
which allows analytics and real-time alerts to the monitoring system administrators. The backend uses a scalable,
offsite-hosted approach allowing administrators to scale the number of networks monitored by scaling the backend 
resources linearly.

The RIVAN network is built on the "Google Cloud" platform and utilizes the following technologies:

1. Traffic Generator (VM #1 --- OS: Ubuntu 18.04 LTS)
    * Kafka Client ([Python Plugin](https://pypi.org/project/kafka-python/))
    * MySQL ([About](https://www.mysql.com/))
    * SQLAlchemy ([Python Plugin](https://pypi.org/project/SQLAlchemy/))
    
2. Kafka Broker (VM #2 --- OS: Ubuntu 18.04 LTS)
    * Kafka ([Apache Site Page](https://kafka.apache.org/))
    
3. Spark Master/Slave (Standalone) (VM #3 --- OS: Ubuntu 18.04 LTS)
    * Spark ([Apache Site Page](https://spark.apache.org/))
    * Pyspark ([Python Plugin](https://pypi.org/project/pyspark/))
    * **Note: Deployed using a [Juju charm](https://jujucharms.com/apache-spark/13)**

4. Spark Slave (VM #4 --- )
    * Spark ([Apache Site Page](https://spark.apache.org/))
    * **Note: Deployed using a [Juju charm](https://jujucharms.com/apache-spark/13)**
    
### Network Configuration

