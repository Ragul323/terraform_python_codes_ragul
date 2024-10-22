import boto3
import logging
from botocore.exceptions import ClientError
# Setup logging
logging.basicConfig(level=logging.INFO)
# Initialize RDS client
rds_client = boto3.client('rds')
def lambda_handler(event, context):
    action = event.get("action")
    instance_names = event.get("instance_names", [])  # Accept multiple instance names
    # Updated RDS instance mapping with lowercase identifiers
    rds_instances = {
        'A': 'rds-instance-a',
        'B': 'rds-instance-b',
        'C': 'rds-instance-c',
        'D': 'rds-instance-d'
    }
    # If no instances are provided, return an error message
    if not instance_names:
        return {"message": "No RDS instances provided."}
    results = []  # To store the result for each instance
    for instance_name in instance_names:
        instance_id = rds_instances.get(instance_name)
        if not instance_id:
            results.append({"message": f"No RDS instance found for {instance_name}"})
            continue
        try:
            # Describe the RDS instance to check its status
            response = rds_client.describe_db_instances(DBInstanceIdentifier=instance_id)
            current_state = response['DBInstances'][0]['DBInstanceStatus']
            logging.info(f"Current state of instance {instance_id}: {current_state}")
            # Perform start/stop based on the action and current state
            if action == "stop" and current_state == "available":
                rds_client.stop_db_instance(DBInstanceIdentifier=instance_id)
                results.append({"message": f"Stopping RDS instance {instance_id}."})
            elif action == "start" and current_state == "stopped":
                rds_client.start_db_instance(DBInstanceIdentifier=instance_id)
                results.append({"message": f"Starting RDS instance {instance_id}."})
            else:
                results.append({"message": f"Action {action} not applicable in current state {current_state} for {instance_id}."})
        except ClientError as e:
            # Check if the error code is DBInstanceNotFound
            if e.response['Error']['Code'] == 'DBInstanceNotFound':
                results.append({"message": f"DB Instance not found: {str(e)} for {instance_id}"})
            else:
                results.append({"message": f"Error occurred: {str(e)} for {instance_id}"})
        except Exception as e:
            results.append({"message": f"Unexpected error occurred: {str(e)} for {instance_id}"})
    return {"results": results}













