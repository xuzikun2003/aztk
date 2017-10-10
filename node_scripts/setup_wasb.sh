#!/bin/bash

# script to install blob storage connection on each node
# Usage:
# setup_wasb.sh [storage_account_name] [storage_account_key]

storage_account_name=$1
storage_account_key=$2
storage_account_suffix=$3

adls_tenant_id=$4
adls_client_id=$5
adls_credential=$6

spark_home=/home/spark-current
cd $spark_home/conf

cp spark-defaults.conf.template spark-defaults.conf

cat >> spark-defaults.conf <<EOF
spark.jars                 $spark_home/jars/azure-storage-2.0.0.jar,$spark_home/jars/hadoop-azure-2.7.3.jar,$spark_home/jars/azure-data-lake-store-sdk-2.0.11.jar,$spark_home/jars/hadoop-azure-datalake-3.0.0-alpha2.jar
EOF

cat >> core-site.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
  <name>fs.AbstractFileSystem.wasb.Impl</name>
  <value>org.apache.hadoop.fs.azure.Wasb</value>
</property>
<property>
  <name>fs.azure.account.key.$storage_account_name.blob.$storage_account_suffix</name>
  <value>$storage_account_key</value>
</property>

<property>
  <name>fs.adl.impl</name>
  <value>org.apache.hadoop.fs.adl.AdlFileSystem</value>
</property>
<property>
  <name>fs.AbstractFileSystem.adl.impl</name>
  <value>org.apache.hadoop.fs.adl.Adl</value>
</property>
<property>
  <name>dfs.adls.oauth2.access.token.provider.type</name>
  <value>ClientCredential</value>
</property>

<property>
  <name>dfs.adls.oauth2.refresh.url</name>
  <value>https://login.microsoftonline.com/$adls_tenant_id/oauth2/token</value>
</property>
<property>
  <name>dfs.adls.oauth2.client.id</name>
  <value>$adls_client_id</value>
</property>
<property>
  <name>dfs.adls.oauth2.credential</name>
  <value>$adls_credential</value>
</property>

</configuration>
EOF

cd $spark_home/jars

# install the appropriate jars
apt install wget
wget http://repo1.maven.org/maven2/com/microsoft/azure/azure-storage/2.0.0/azure-storage-2.0.0.jar
wget http://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure/2.7.3/hadoop-azure-2.7.3.jar
wget http://central.maven.org/maven2/org/apache/hadoop/hadoop-azure-datalake/3.0.0-alpha2/hadoop-azure-datalake-3.0.0-alpha2.jar
wget http://central.maven.org/maven2/com/microsoft/azure/azure-data-lake-store-sdk/2.0.11/azure-data-lake-store-sdk-2.0.11.jar
