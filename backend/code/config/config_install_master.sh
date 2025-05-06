#!/bin/bash

# Update package list and install Python pip
apt-get update
apt-get install -y python3-pip

# Install necessary Python packages
python3 -m pip install pyspark==3.0.0 numpy

$SPARK_HOME/sbin/start-master.sh

tail -f /dev/null