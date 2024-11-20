import boto3
import json
eks_client = boto3.client('eks')
asg_client = boto3.client('autoscaling')
def get_auto_scaling_group(cluster_name, nodegroup_name):
    """Fetch the Auto Scaling Group name for the node group."""
    try:
        response = eks_client.describe_nodegroup(
            clusterName=cluster_name,
            nodegroupName=nodegroup_name
        )
        return response['nodegroup']['resources']['autoScalingGroups'][0]['name']
    except Exception as e:
        raise Exception(f"Error fetching ASG for {nodegroup_name}: {e}")
def save_scaling_configuration(asg_name):
    """Save the current scaling configuration as a tag."""
    try:
        response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        asg_info = response['AutoScalingGroups'][0]
        scaling_config = {
            "min_size": asg_info['MinSize'],
            "max_size": asg_info['MaxSize'],
            "desired_capacity": asg_info['DesiredCapacity']
        }
        # Store the scaling config as a tag
        asg_client.create_or_update_tags(
            Tags=[
                {
                    "ResourceId": asg_name,
                    "ResourceType": "auto-scaling-group",
                    "Key": "scaling_config",
                    "Value": json.dumps(scaling_config),
                    "PropagateAtLaunch": False
                }
            ]
        )
        print(f"Scaling configuration saved for {asg_name}: {scaling_config}")
    except Exception as e:
        raise Exception(f"Error saving scaling configuration for {asg_name}: {e}")
def restore_scaling_configuration(asg_name):
    """Restore the scaling configuration from the tag."""
    try:
        response = asg_client.describe_tags(Filters=[{"Name": "auto-scaling-group", "Values": [asg_name]}])
        scaling_config_tag = next(
            (tag for tag in response['Tags'] if tag['Key'] == 'scaling_config'),
            None
        )
        if not scaling_config_tag:
            raise Exception(f"No scaling configuration tag found for {asg_name}")
        scaling_config = json.loads(scaling_config_tag['Value'])
        # Restore the scaling configuration
        asg_client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MinSize=scaling_config['min_size'],
            MaxSize=scaling_config['max_size'],
            DesiredCapacity=scaling_config['desired_capacity']
        )
        print(f"Scaling configuration restored for {asg_name}: {scaling_config}")
    except Exception as e:
        raise Exception(f"Error restoring scaling configuration for {asg_name}: {e}")
def stop_cluster(cluster_name, nodegroup_name):
    """Stop a cluster by setting desired capacity to 0 and saving the scaling config."""
    try:
        asg_name = get_auto_scaling_group(cluster_name, nodegroup_name)
        save_scaling_configuration(asg_name)
        asg_client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MinSize=0,
            DesiredCapacity=0
        )
        print(f"Cluster {cluster_name} stopped successfully.")
    except Exception as e:
        raise Exception(f"Error stopping cluster {cluster_name}: {e}")
def start_cluster(cluster_name, nodegroup_name):
    """Start a cluster by restoring its scaling configuration."""
    try:
        asg_name = get_auto_scaling_group(cluster_name, nodegroup_name)
        restore_scaling_configuration(asg_name)
        print(f"Cluster {cluster_name} started successfully.")
    except Exception as e:
        raise Exception(f"Error starting cluster {cluster_name}: {e}")
def check_dependencies(cluster_name, action):
    """Check cluster dependencies before performing start or stop actions."""
    dependencies = {
        "ragul": ["arun", "yuvi", "durga"],
        "arun": [],
        "yuvi": [],
        "durga": []
    }
    if action == "stop":
        for dependent in dependencies.get(cluster_name, []):
            dependent_asg_name = get_auto_scaling_group(dependent, f"{dependent}_nodegroup")
            asg_info = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[dependent_asg_name])
            if asg_info['AutoScalingGroups'][0]['DesiredCapacity'] > 0:
                raise Exception(f"Cannot stop {cluster_name} while {dependent} is running.")
    elif action == "start":
        for main, dependents in dependencies.items():
            if cluster_name in dependents:
                main_asg_name = get_auto_scaling_group(main, f"{main}_nodegroup")
                asg_info = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[main_asg_name])
                if asg_info['AutoScalingGroups'][0]['DesiredCapacity'] == 0:
                    raise Exception(f"Cannot start {cluster_name} while {main} is stopped.")
def lambda_handler(event, context):
    """AWS Lambda function entry point."""
    try:
        cluster_name = event["cluster_name"]
        nodegroup_name = event["nodegroup_name"]
        action = event["action"]
        # Check dependencies
        check_dependencies(cluster_name, action)
        if action == "stop":
            stop_cluster(cluster_name, nodegroup_name)
        elif action == "start":
            start_cluster(cluster_name, nodegroup_name)
        else:
            raise Exception(f"Invalid action: {action}")
        return {
            "statusCode": 200,
            "message": f"{action.capitalize()} operation completed for {cluster_name}."
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "message": str(e)
        }
