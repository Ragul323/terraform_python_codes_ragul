import boto3
import os
def lambda_handler(event, context):
    eks_client = boto3.client('eks')
    cluster_name = os.environ['EKS_CLUSTER_NAME']
    # Get node group details
    response = eks_client.describe_nodegroup(
        clusterName=cluster_name,
        nodegroupName='worker_node_test'  # Change this to your node group name
    )
    # Get tags to retrieve the old configuration
    tags = eks_client.list_tags_for_resource(
        resourceArn=response['nodegroup']['nodegroupArn']
    )['tags']
    old_desired_size = int(tags.get('old_desired_size', 1))
    old_min_size = int(tags.get('old_min_size', 1))
    old_max_size = int(tags.get('old_max_size', 1))
    # Update node group with old scaling configuration
    eks_client.update_nodegroup_config(
        clusterName=cluster_name,
        nodegroupName='worker_node_test',
        scalingConfig={
            'desiredSize': old_desired_size,
            'minSize': old_min_size,
            'maxSize': old_max_size
        }
    )
    return {
        'statusCode': 200,
        'body': "Worker nodes started with previous configuration."
    }
