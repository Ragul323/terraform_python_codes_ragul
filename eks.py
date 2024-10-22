import boto3 
def scale_down_eks_workers(cluster_name, desired_capacity=0, region_name='ap-south-1'):
    # Initialize the boto3 client for Auto Scaling and EKS
    autoscaling_client = boto3.client('autoscaling', region_name=region_name)
    eks_client = boto3.client('eks', region_name=region_name)
    # Get the EKS cluster details
    response = eks_client.describe_cluster(name=cluster_name)
    cluster = response['cluster']
    # Get the Auto Scaling groups associated with the EKS cluster
    asg_name_prefix = f"eks-{cluster_name}-nodegroup"
    # Describe Auto Scaling groups with matching name patterns
    asg_response = autoscaling_client.describe_auto_scaling_groups()
    # Find the ASG that corresponds to the EKS worker nodes
    asg_names = []
    for asg in asg_response['AutoScalingGroups']:
        if asg_name_prefix in asg['AutoScalingGroupName']:
            asg_names.append(asg['AutoScalingGroupName'])
    if not asg_names:
        print("No Auto Scaling Groups found for the EKS worker nodes.")
        return
    # Scale down each Auto Scaling Group to the desired capacity 
    for asg_name in asg_names:
        print(f"Scaling down Auto Scaling Group: {asg_name} to {desired_capacity} instances")
        autoscaling_client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=desired_capacity,
            MinSize=desired_capacity
        )
    print("EKS worker nodes scaling down...")
# Usage
cluster_name = 'your-cluster-name'  # Replace with your cluster name
desired_capacity = 0  # Set the desired capacity (0 to stop all workers)
scale_down_eks_workers(cluster_name, desired_capacity)



