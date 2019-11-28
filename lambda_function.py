from __future__ import print_function

import json
import boto3

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sgCommon = "sg-0e7229b92b492ad7c"

client = boto3.client('ec2')
ec2R = boto3.resource('ec2')

# Change debugMode to True to debug
debugMode = False
      
DRYRUN = False
if (debugMode):
  logger.setLevel(logging.DEBUG)
  DRYRUN = True

def lambda_handler(event, context):
  logger.info(event)
  if ("detail" in event and "event" in event['detail'] and event['detail']['event'] == "createVolume" ):
    if (event['detail']['result'] != "available"):
      logger.error("Volume not ready")
    else:
      #logger.info("EC {0} start maange security-group".format(ec2instance.id) )
      logger.info("Volume ready")
    
    # Get volume from event
    ressources = event['resources'][0]
    arn,volumeID = ressources.split(":volume/")
    volume = ec2R.Volume(volumeID)
    
    # Get EC2 attached instance ID 
    if  len(volume.attachments) == 0:
      logger.info("Volume {0} not attached to an EC2 instance".format(volumeID))
      return False
    else:
      EC2Id=volume.attachments[0]['InstanceId']
      ec2instance = ec2R.Instance(EC2Id)
      
    # Ensure it's volume of cloud9 environment
    isC9=False
    for tags in ec2instance.tags:
      if tags["Key"] == 'aws:cloud9:environment':
        isC9 = True

    if isC9:
      logger.info("EC instance of cloud9 found: {0}. Start manage security-group".format(ec2instance.id))
      all_sg_ids = [sg['GroupId'] for sg in ec2instance.security_groups]  # Get a list of ids of all securify groups attached to the instance
      if sgCommon not in all_sg_ids:
        # Assign only the common security group.
        response = ec2instance.modify_attribute(Groups=[sgCommon])
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
          logger.info("EC {0} common security group assigned: {1}".format(ec2instance.id, sgCommon))
        else:
          logger.error("EC {0} error when trying to assign common security group: {1}. Responde: {2}".format(ec2instance.id, sgCommon, response))
      else:
        logger.info("EC {0} assign common security group {1} skipped: already attached.".format(ec2instance.id, sgCommon) )
        
      for sg_id in all_sg_ids :
        response = client.delete_security_group(GroupId=sg_id)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
          logger.info("EC {0} old security group {1} deleted.".format(ec2instance.id, sg_id))
        else:
          logger.error("EC {0} error when trying to delete old security group {1}. Responde: {2}".format(ec2instance.id, sg_id, response))
    else:
      logger.info("EC {0} manage security-group skipped: not a cloud9 environment".format(volumeID))
      return False

    logger.info("EC {0} manage security-group finished".format(ec2instance.id))
    return True