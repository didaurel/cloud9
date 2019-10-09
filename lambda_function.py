import boto3
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
  print ('Start')
  region = 'eu-west-1'
  client = boto3.client('ec2', region_name=region)
  filters = [{
        'Name': 'tag:Name',
        'Values': ['packer-build*']
    },
    {
        'Name': 'instance-state-name', 
        'Values': ['stopped']
    }
  ]
  
  ec2 = boto3.resource('ec2')
  instances = ec2.instances.filter(Filters=filters)
  
  instanceToDelele = []
  for instance in instances:
    instanceToDelele.append(instance.id)
    
  response = client.terminate_instances(InstanceIds=instanceToDelele)
  
  i = 0
  for instance in response['TerminatingInstances']:
    i += 1
    logger.debug("EC2 Packer Instance {0} terminated. Current status: {1}".format(instance['InstanceId'], instance['CurrentState']['Name']))

  logger.info("EC2 Packer Instances terminated total: {0}".format(i))

  