import boto3
import os
def lambda_handler(event, context):
    eks_client = boto3.client('eks')
    autoscaling_client = boto3.client('autoscaling')
    cluster_name = os.environ['EKS_CLUSTER_NAME']
    # Get node group details
    response = eks_client.describe_nodegroup(
        clusterName=cluster_name,
        nodegroupName='worker_node_test'  # Change this to your node group name
    )
    current_desired_size = response['nodegroup']['scalingConfig']['desiredSize']
    current_min_size = response['nodegroup']['scalingConfig']['minSize']
    current_max_size = response['nodegroup']['scalingConfig']['maxSize']
    # Tag the cluster with the old configuration
    tags = {
        'old_desired_size': str(current_desired_size),
        'old_min_size': str(current_min_size),
        'old_max_size': str(current_max_size)
    }
    eks_client.tag_resource(
        resourceArn=response['nodegroup']['nodegroupArn'],
        tags=tags
    )
    # Update the node group to stop worker nodes (desiredSize=0)
    eks_client.update_nodegroup_config(
        clusterName=cluster_name,
        nodegroupName='worker_node_test',
        scalingConfig={
            'desiredSize': 0,
            'minSize': 0,
            'maxSize': 1
        }
    )
    return {
        'statusCode': 200,
        'body': "Worker nodes stopped. Old configuration stored in tags."
    }









