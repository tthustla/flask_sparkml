#! /bin/bash
#update the package list
sudo apt-get update
#install JDK8 and PIP
# sudo apt-get install -y openjdk-8-jdk python-pip python-dev build-essential
sudo apt-get install -y openjdk-8-jdk python-pip
#install required Python packages using pip
#pyspark uses --no-cache-dir option to prevent memory error due to the big packae size
pip install Flask==0.12.2 pyspark==2.3.0 --no-cache-dir flask-restful==0.3.7 numpy==1.15.3
