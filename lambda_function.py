import boto3
import datetime
import os
import requests

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ec2_cli = boto3.client('ec2')

#List european zone
regions = []
regions_cli = ec2_cli.describe_regions()["Regions"]

for region in regions_cli:
    regions.append(region["RegionName"])

def lambda_handler(event, context):
    
    count = 0
    message = ""
    
    #Set date - 8 hours
    start_date = datetime.datetime.today() - datetime.timedelta(hours=8)
    print("Start " + str(start_date))
    
    for region in regions :
        
        ec2_res = boto3.resource('ec2', region_name = region)
        #####Get EC2
        #Filter get running ec2
        filters = [
            {
                'Name': 'instance-state-name', 
                'Values': ['running']
            }
        ]
        
        #Get instances by filters
        instances = ec2_res.instances.filter(Filters=filters)
        ec2_list = []
        
        regionReport = ""
        #Parse all instances which are running or stopped
        for instance in instances :
            if(instance.launch_time.replace(tzinfo=None) < start_date):
                cloud9 = False
                name = ""
                for j in range(len(instance.tags)):
                    if instance.tags[j]["Key"] == "Name":
                        name = instance.tags[j]["Value"]
                    if instance.tags[j]["Key"] == "aws:cloud9:environment":
                        cloud9 = True
                if cloud9 :
                    count = count + 1
                    instance_description  = " --> " + name + " (" + instance.id + " / " + str(instance.launch_time) + ") : " + instance.instance_type + "\n"
                    logger.info(instance_description)
                    regionReport = regionReport + instance_description
        if not regionReport == "":
            message = "### " + region + " \n" + regionReport + message
    
    if not message == "" :
        message = "These " + str(count) + " Cloud9 have been started since more than 8 hours :\n" + message
        message = "######################\n" + message
    
        print(message)
        logger.debug ("Message: {0}".format(message))
        logger.info ("Send slack message...")
        result = sendSlackMessage(message)
        #result = 200

        if result == 200:
            logger.info ("Slack notification sent.")
        else:
            logger.error ("Slack notification error, return code: %d" % (result))
    
def sendSlackMessage (message) :
    SLACK_URL=os.environ['webhook_URL']
    SLACK_CHANNEL=os.environ['channel']
    SLACK_USERNAME=os.environ['username']
    SLACK_ICON=os.environ['icon_emoji']
    try:
        response = { "text" : message, "channel": SLACK_CHANNEL, "username": SLACK_USERNAME, "icon_emoji": SLACK_ICON}
        slack_response = requests.post(SLACK_URL,json=response, headers={'Content-Type': 'application/json'})
        return slack_response.status_code
    except Exception as inst:
        logger.error ("Slack Callout Failed.Message: '%s'" % (inst))
        return 0