import boto3
ec2R = boto3.resource('ec2')
ec2 = boto3.client('ec2')
c9 = boto3.client('cloud9')

from botocore.exceptions import ClientError

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

debugMode = False

DRYRUN = False
if (debugMode):
  logger.setLevel(logging.DEBUG)
  DRYRUN = True

EBS_SIZE = 20
EBS_SIZE_DG = {'EAC': 40}

def lambda_handler(event, context):
  if (event['detail']['event'] == "createVolume" ):
    if (event['detail']['result'] != "available"):
      logger.error("Volume not ready")
    else:
      # Get volume from event
      ressources = event['resources'][0]
      arn,volumeID = ressources.split(":volume/")
      volume = ec2R.Volume(volumeID)
      logger.info("Volume {0} start resize".format(volumeID) )
      
      # Get EC2 attached instance ID 
      if  len(volume.attachments) == 0:
        logger.info("Volume {0} skipped, not attached to an EC2 instance".format(volumeID))
        return False
      else:
        EC2Id=volume.attachments[0]['InstanceId']
        ec2instance = ec2R.Instance(EC2Id)
      
      # Ensure it's volume of cloud9 environment
      isC9=False
      for tags in ec2instance.tags:
        if tags["Key"] == 'aws:cloud9:environment':
          isC9 = True
          # if 'noebsresize' is present on description, don't resize volume
          response = c9.describe_environments(environmentIds=[tags["Value"]])
          c9env  = response['environments'][0]
          if "noebsresize" in c9env['description'].lower():
            logger.info("Volume {0} skipped: 'noebsresize' found on C9 description".format(volumeID))
            return False
          break;
          
      if isC9:
        # Call tagEC2InstancesAndVolumes lambda to have DG tag available
        lambdaC = boto3.client('lambda')
        response = lambdaC.invoke(
          FunctionName='tagEC2InstancesAndVolumes',
          InvocationType='RequestResponse',
          Payload='{"instanceId" : "'+ EC2Id +'"}'
        )
        logger.info("tagEC2InstancesAndVolumes called for EC2Id '{0}'. Response: {1}".format(EC2Id, response) )
        # Reload volume after tagging
        volume = ec2R.Volume(volumeID)

        # Get DG tag of volume
        for tags in volume.tags:
          if tags["Key"] == 'DG':
            tagDG = tags["Value"]

        # Get new size by DG
        newSize = EBS_SIZE
        if tagDG in EBS_SIZE_DG:
          newSize=EBS_SIZE_DG[tagDG]
          logger.info("Volume {0} have DG '{1}', resize value: {2}Go".format(volumeID, tagDG, newSize) )

        curSize = volume.size
        if curSize >= newSize:
        # Size Ok, skip
          logger.info("Volume {0} skipped: size OK: {1}Go".format(volumeID, curSize) )
        else:
        # Edit Volume
          response = False
          try:
            response = ec2.modify_volume(
                DryRun=DRYRUN,
                VolumeId=volumeID,
                Size=newSize
            )
          except ClientError as e:
            logger.debug(e)
            #An error occurred (VolumeModificationRateExceeded) when calling the ModifyVolume operation: You've reached the maximum modification rate per volume limit. Wait at least 6 hours between modifications per EBS volume.
            logger.error("Volume {0} failed: ClientError Exception: {1}".format(volumeID, e))
            return False
          if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info("Volume {0} updated: size changed from {1}Go to {2}Go".format(volumeID, curSize, newSize))
            return True
          else:
            logger.error("Volume {0} failed: Target {1}Go, Current Size: {2}. Responde: {3}".format(volumeID, newSize,curSize, response))
      else:
        logger.info("Volume {0} skipped: not cloud9 environment".format(volumeID))
  return False
