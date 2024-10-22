import json
import boto3
import os
def lambda_handler(event, context):
    rds_client = boto3.client('rds')
    rds_instance_id = os.environ['RDS_INSTANCE_ID']
    try:
        response = rds_client.stop_db_instance(DBInstanceIdentifier=rds_instance_id)
        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully stopped RDS instance {rds_instance_id}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error stopping RDS instance: {str(e)}')
        }