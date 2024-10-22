import json
import boto3
import os
def handler(event, context):
    rds_client = boto3.client('rds')
    rds_instance_id = os.environ['RDS_INSTANCE_ID']
    action = event.get('action')   
    if action == 'start':
        try:
            response = rds_client.start_db_instance(DBInstanceIdentifier=rds_instance_id)
            return {
                'statusCode': 200,
                'body': json.dumps(f'Starting RDS instance {rds_instance_id}')
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error starting RDS instance: {str(e)}')
            }
    elif action == 'stop':
        try:
            response = rds_client.stop_db_instance(DBInstanceIdentifier=rds_instance_id)
            return {
                'statusCode': 200,
                'body': json.dumps(f'Stopping RDS instance {rds_instance_id}')
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error stopping RDS instance: {str(e)}')
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid action. Use "start" or "stop".')
        }

# -----------------------------------------------------------#
   to convert zip "sudo zip -r lambda_function.zip index.py "