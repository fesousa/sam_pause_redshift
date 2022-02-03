import json
import time
import boto3
from botocore.exceptions import ClientError
import datetime
import os
import sys

def lambda_handler(event, context):
    client = boto3.client('redshift')
    cron = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
    try:
        all_clusters = client.describe_clusters(
            ClusterIdentifier=''
        )
        if all_clusters is not None:
            for i, cluster in enumerate(all_clusters["Clusters"]):
                clusterId = cluster["ClusterIdentifier"]
                #snapId = f'snapshot-{clusterId}-{(datetime.datetime.now()).strftime("%Y%m%d%H%M%S")}'
                snapId = f'snapshot-{clusterId}'
                try:
                    response = client.create_cluster_snapshot(
                                    SnapshotIdentifier=snapId,
                                    ClusterIdentifier=clusterId,
                                    ManualSnapshotRetentionPeriod=1
                                )
                except:
                    pass
                status = ''
                while status != 'available':
                    response = client.describe_cluster_snapshots(
                        SnapshotIdentifier=snapId                    
                    )
                    status = response['Snapshots'][0]['Status']
                    print("Verificando snap:", status)
                    time.sleep(30)
                triesPause = 0
                while triesPause < 30:
                    try:
                        response = client.pause_cluster(ClusterIdentifier=clusterId)
                        break
                    except:
                        print('Tentando pausar...')
                        triesPause+=1
                        time.sleep(30)
    except ClientError as e:
        print(f'ERROR: {e}')
        return "Erro"
    else:
        return ("OK")