import boto3
import json
# Define the mapping between names and database instances
name_to_db_mapping = {
    'Ragul': ['database-a'],
    'Ravi': ['database-b','database-c'],
    'Yuvi': ['database-d'],
    # You can extend this mapping with more names and databases if needed
}
def lambda_handler(event, context):
    # Get the list of names from the event
    names = event.get('names', [])
    action = event.get('action', '').lower()
    # Check if the action is provided
    if action not in ['start', 'stop']:
        return {
            'statusCode': 400,
            'body': 'Please provide a valid "action" ("start" or "stop").'
        }
    # Check if at least one name is provided
    if not names:
        return {
            'statusCode': 400,
            'body': 'Please provide at least one name in the "names" field.'
        }
    # List all available RDS instances for debugging
    rds_client = boto3.client('rds')
    try:
        instances = rds_client.describe_db_instances()
        available_db_instances = [db['DBInstanceIdentifier'] for db in instances['DBInstances']]
        print(f"Available RDS Instances: {available_db_instances}")
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error retrieving RDS instances: {str(e)}"
        }
    # Create a Lambda client to invoke the start/stop function
    lambda_client = boto3.client('lambda')
    # Loop through the names and process each one
    for name in names:
        # Check if the name exists in the mapping
        if name not in name_to_db_mapping:
            return {
                'statusCode': 404,
                'body': f'No database found for the name "{name}". Available RDS instances: {available_db_instances}'
            }
        # Get the corresponding database instances for the name
        db_instances = name_to_db_mapping[name]
        print(f"Databases for {name}: {db_instances}")
        # Check if the mapped databases are in the available RDS instances
        for db_instance in db_instances:
            if db_instance not in available_db_instances:
                return {
                    'statusCode': 404,
                    'body': f"Database '{db_instance}' mapped to '{name}' not found in available RDS instances."
                }
        # Loop through each database instance and invoke the start/stop function
        for db_instance_id in db_instances:
            payload = {
                'instance_id': db_instance_id,
                'action': action
            }
            # Invoke the start/stop Lambda function for each database
            try:
                response = lambda_client.invoke(
                    FunctionName='arn:aws:lambda:ap-south-1:183631326320:function:start_stop_rds',  # Replace with the name or ARN of the first Lambda function
                    InvocationType='Event',  # Use 'Event' for async invocation
                    Payload=json.dumps(payload)  # Convert Python dict to JSON
                )
            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': f"Error invoking start/stop Lambda for {db_instance_id}: {str(e)}"
                }
    return {
        'statusCode': 200,
        'body': f'Triggered action "{action}" on databases for names: {names}.'
    }