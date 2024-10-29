import json
def lambda_handler(event, context):
    # Define your name to database mapping
    name_to_db_mapping = {
        "Arun": "database-a",
        "Navin": "database-b",
        "Ragul": "database-c",
        "Shubha": "database-d"
    }
    return {
        'statusCode': 200,
        'body': json.dumps(name_to_db_mapping)
    }