import copy

import os
import os.path
import sys

#envLambdaTaskRoot = os.environ["LAMBDA_TASK_ROOT"]
#print("LAMBDA_TASK_ROOT env var:"+os.environ["LAMBDA_TASK_ROOT"])
#print("sys.path:"+str(sys.path))

#sys.path.insert(0,envLambdaTaskRoot+"/tagInstancesAndVolumes")
#print("sys.path:"+str(sys.path))
import botocore
import boto3

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

debugMode = False
# Pattern used to rename EC2 Instance
EC2InstanceNamePattern = 'aws-cloud9-{Cloud9Name}-{Cloud9EnvId}'

if (debugMode):
  logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
  logger.debug("boto3 version:"+boto3.__version__)
  logger.debug("botocore version:"+botocore.__version__)

  instanceId = None
  if 'instanceId' in event:
    instanceId = event['instanceId']
    logger.debug("Instance ID provided: " + instanceId)

  tagEC2Instances(instanceId, context);

  # Tag Unused volume separatly
  if instanceId == None:
    tagUnusedEC2Volumes(event, context);

  return 'Done'

# Rename EC2 instance of cloud9 environements
def tagEC2Instances(instanceId, context):
  logger.info('Start tag EC2 Instances and volumes...')
  totalInstanceDone = 0
  totalInstanceSkipped = 0
  totalVolumeDone = 0
  totalVolumeSkipped = 0
  
  cloud9 = boto3.client('cloud9')
  ec2 = boto3.resource('ec2')
  ec2Client = boto3.client('ec2')
  
  # Pre-load users to avoid 1 call by EC2 instance
  usersByID = getUsersByUserID()
  
  # Pre-load volumes to avoid 1 call by EC2 instance
  volumes = {}
  for vol in ec2.volumes.filter(Filters=[{'Name': 'status','Values': ['in-use', 'creating']}], MaxResults=50): 
    volumes[vol.volume_id] = vol

  # if None, tag all instances
  if instanceId == None:
    filters = [{
        'Name': 'tag:Name',
        'Values': ['aws-cloud9-*']
      },
    ]
  else:
    filters=[{
      'Name': 'instance-id',
      'Values': [instanceId]
    }]

  filters.append({
        'Name': 'instance-state-name', 
        'Values': ['pending','running','shutting-down','stopping','stopped']
  })

  for instance in ec2.instances.filter(Filters=filters, MaxResults=50):
    logger.debug("--------------------------------------------------------")
    logger.debug("EC2 Instance `" + instance.instance_id + "`: start update tags `name`, `DG`...")
    
    EC2_Cloud9EnvId = [tag['Value'] for tag in instance.tags if tag['Key'] == 'aws:cloud9:environment']
    
    if  len(EC2_Cloud9EnvId) > 0:
      # Define newName using EC2InstanceNamePattern
      EC2_Cloud9EnvId = EC2_Cloud9EnvId[0]
      EC2_Cloud9 = cloud9.describe_environments(environmentIds=[EC2_Cloud9EnvId])["environments"][0]
      EC2_Cloud9Name = EC2_Cloud9['name']
      newName = EC2InstanceNamePattern.format(Cloud9Name=EC2_Cloud9Name, Cloud9EnvId=EC2_Cloud9EnvId)
      # Get DG tag from Instance Owner 
      dgName = "undefined"
      EC2CloudOwner = [tag['Value'] for tag in instance.tags if tag['Key'] == 'aws:cloud9:owner']

      # Workaround: Use client.describe_tags to get tags if owner not found
      # because sometime all tags are not retrieved with instance.tags.
      if (len(EC2CloudOwner) == 0):
        logger.warning ('EC2 instance `{0}`: `aws:cloud9:owner` tag not found, try with describe_tags function'.format(instance.instance_id))
        response = ec2Client.describe_tags(Filters=[{'Name': 'resource-id','Values': [instance.instance_id]}])
        EC2CloudOwner = [tag['Value'] for tag in response['Tags'] if tag['Key'] == 'aws:cloud9:owner']

      if (len(EC2CloudOwner) > 0):
        EC2CloudOwner = EC2CloudOwner[0]
        if (EC2CloudOwner in usersByID):
          dgName = usersByID[EC2CloudOwner]["Tags"]['DG']
        else:
          logger.warning ('EC2 instance `{0}`: User `{1}` not found'.format(instance.instance_id, EC2CloudOwner))
      else:
        logger.warning ('EC2 instance `{0}`: Tag `aws:cloud9:owner` not found'.format(instance.instance_id))

      # Get current tag and add new calculated tags
      cur_tags = boto3_tag_list_to_ansible_dict(instance.tags)
      new_tags = copy.deepcopy(cur_tags)
      new_tags['Name'] = newName
      new_tags['DG'] = dgName
      new_tags['Project'] = dgName
        
      # Set tag only if changed
      if new_tags != cur_tags:
        totalInstanceDone += 1;
        instance.create_tags(DryRun=debugMode, Tags=ansible_dict_to_boto3_tag_list(new_tags))
        logger.info('EC2 instance `{0}`: tags updated to `{1}`'.format(instance.instance_id, new_tags))
      else:
        totalInstanceSkipped += 1;
        logger.debug("EC2 instance `" + instance.instance_id + "`: update tag skipped" )
        
      # Set Tags for attached volumes of EC2 Instance
      logger.debug("EC2 instance `{0}`: start update tag of attached volumes...".format(instance.instance_id) )
      for device in instance.block_device_mappings:
        volume = volumes[device['Ebs']['VolumeId']]
        logger.debug('EC2 Volume `{0}`: start update tags `name`, `DG`...'.format(volume.volume_id))
        
        # Get current tag and add new calculated tags (same that EC2 instances)
        cur_tags = boto3_tag_list_to_ansible_dict(volume.tags)
        new_tags = copy.deepcopy(cur_tags)
        new_tags['Name'] = newName
        new_tags['DG'] = dgName
        new_tags['Project'] = dgName
        
        # Set tag only if changed
        if new_tags != cur_tags:
          totalVolumeDone +=1
          logger.info('EC2 Volume `{0}`: tags updated to {1}'.format(volume.volume_id, new_tags))
          volume.create_tags(Tags=ansible_dict_to_boto3_tag_list(new_tags))
        else:
          totalVolumeSkipped +=1
          logger.debug('EC2 Volume `{0}`: update tag skipped'.format(volume.volume_id))
    else:
      totalInstanceSkipped += 1;
      logger.debug("EC2 instance `" + instance.instance_id + "`: not attached to cloud9 environment, update tags skipped" )
      
  
  logger.info("End of tag EC2 Instances and volumes.\ntotalInstanceDone: {0}. totalInstanceSkipped: {1}.\n"  
      "totalVolumeDone: {2}. totalVolumeDone: {3}.".format(totalInstanceDone, totalInstanceSkipped, totalVolumeDone, totalVolumeSkipped) )

  return True
  
# Rename unused EC2 volume
def tagUnusedEC2Volumes(event, context):
  totalRenameDone = 0
  totalUnused = 0
 
  volumes = {}
  logger.info('Start tagUnusedEC2Volumes...')
  filters = [{
      'Name': 'status',
      'Values': ['available']
    }
  ]
  ec2 = boto3.resource('ec2')
  volumes = ec2.volumes.filter(Filters=filters)
  for volume in volumes:
    totalUnused += 1
    logger.debug('EC2 Volume `{0}`: not attached to EC2Instance'.format(volume.volume_id))
    if (volume.tags):
      name = [tag['Value'] for tag in volume.tags if tag['Key'] == 'Name'][0]
    else:
      name=volume.volume_id
        
    if not name.startswith('UNUSED'):
      newName = 'UNUSED ' + name
      volume.create_tags(DryRun=debugMode, Tags=[{'Key': 'Name', 'Value': newName}])
      totalRenameDone += 1;
      logger.info('EC2 Volume `{0}`: Name updated to `{1}`'.format(volume.volume_id, newName))

  logger.info("End of tagUnusedEC2Volumes. totalRenameDone: {0}. TotalUnused: {1}".format(totalRenameDone, totalUnused))
  
  return True

def boto3_tag_list_to_ansible_dict(tags_list):
  tags_dict = {}
  if tags_list is None:
    return tags_dict
  for tag in tags_list:
    if 'key' in tag and not tag['key'].startswith('aws:'):
      tags_dict[tag['key']] = tag['value']
    elif 'Key' in tag and not tag['Key'].startswith('aws:'):
      tags_dict[tag['Key']] = tag['Value']
  return tags_dict

def ansible_dict_to_boto3_tag_list(tags_dict):
  tags_list = []
  for k, v in tags_dict.items():
    tags_list.append({'Key': k, 'Value': v})

  return tags_list

# Return User with tag in sorted array by UserID
def getUsersByUserID ():
  # Cannot user resource IAM, because user.tags is always EMPTY ('none'). Example:
  
  #iam = boto3.resource('iam')
  #allUsers = iam.users.all()
  #for user in allUsers:
  #      print (user.tags)

  # Cannot user client IAM, because user in list_users don't have "keys" attribute.... Example:
  
  #iam = boto3.client('iam')
  #UserByUIserId = {}
  #users = iam.list_users()
  #for user in users['Users']:
  #  print (user)
      
  iamClient = boto3.client('iam')
  UserByUIserId = {}
  IsTruncated  = True
  uMarker = ""
  allUsers = iamClient.list_users(MaxItems=50)
  while IsTruncated == True:
    for user in allUsers['Users']:
        UserByUIserId[user['UserId']] = user
        response = iamClient.list_user_tags(
            UserName=user['UserName']
        )
        UserByUIserId[user['UserId']]['Tags'] = boto3_tag_list_to_ansible_dict(response['Tags'])
    IsTruncated = allUsers['IsTruncated']
    if IsTruncated:
        uMarker = allUsers['Marker']
        allUsers = iamClient.list_users(Marker=uMarker, MaxItems=50)
        
  return UserByUIserId
