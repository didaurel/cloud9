import json
import boto3

region = 'eu-west-1'
client = boto3.client('ec2', region_name=region)
def lambda_handler(event, context):
    TagFilters = [{
            'Name': 'tag:aws:cloudformation:logical-id',
            'Values': ['Instance']
        },
        {
            'Name': 'instance-state-name', 
            'Values': ['running','pending','stopped']
        }
    ]
    InstanceFilter=client.describe_instances(Filters=TagFilters)
    for Reservations in range(len(InstanceFilter['Reservations'])):
        for Instances in range(len(InstanceFilter['Reservations'][Reservations]['Instances'])):
            if not 'IamInstanceProfile' in InstanceFilter['Reservations'][Reservations]['Instances'][Instances].keys():
                response = client.associate_iam_instance_profile(
                    IamInstanceProfile={
                        'Arn': 'arn:aws:iam::469132580751:instance-profile/Cloud9Role',
                        'Name': 'Cloud9Role'
                    },
                        InstanceId=InstanceFilter['Reservations'][Reservations]['Instances'][Instances]['InstanceId']
                )
                print("Role assigned to "+InstanceFilter['Reservations'][Reservations]['Instances'][Instances]['InstanceId'])