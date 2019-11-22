import json
import boto3
import datetime
import os
import ConfigParser
from botocore.vendored import requests

START_DATE = 60

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ec2_cli = boto3.client('ec2')
accountName = "Test"
if "Account" in os.environ.keys():
    accountName = os.environ['Account']
    
#List european zone
regions = []
regions_cli = ec2_cli.describe_regions()["Regions"]

for region in regions_cli:
    regions.append(region["RegionName"])

def lambda_handler(event, context):
    
    count = 0
    message = ""
    
    #Set date using START_DATE
    start_date = datetime.datetime.today() - datetime.timedelta(days=START_DATE)
    logger.info ("Check instances stated before " + start_date.strftime("%A %d. %B %Y"))
    for region in regions :
        
        ec2_res = boto3.resource('ec2', region_name = region)
        #####Get EC2
        #Filter get stopped ec2
        filters = [
            {
                'Name': 'instance-state-name', 
                'Values': ['stopped']
            }
        ]
        
        #Get instances by filters
        instances = ec2_res.instances.filter(Filters=filters)
        ec2_list = []
        
        regionReport = ""
        #Parse all instances which are running or stopped
        for instance in instances :
            stopDate = ""
            when = instance.state_transition_reason.split("(")
            if len(when) > 1 :
                stopDate = when[1].replace(")","").split(" ")[0]
            if stopDate != "" :
                if  datetime.datetime.strptime(stopDate, "%Y-%m-%d") < start_date :
                #if(instance.launch_time.replace(tzinfo=None) < start_date):
                    count = count + 1
                    name = ""
                    for j in range(len(instance.tags)):
                        if instance.tags[j]["Key"] == "Name":
                            name = instance.tags[j]["Value"]
                    #instance_description  = " --> " + name + " (" + instance.id + " / " + str(instance.launch_time.date()) + ") : " + instance.instance_type + "\n"
                    instance_description  = unichr(8226) + " " + name + " (" + instance.id + " / " + stopDate + ") : " + instance.instance_type + "\n"
                    logger.info(instance_description)
                    regionReport = regionReport + instance_description
        if not regionReport == "":
            message = region.upper() + " \n" + regionReport + message
    
    if not message == "" :
        message = "These " + str(count) + " instances have been stopped since more than "+ str(START_DATE) + " days:\n" + message
        message = message + "\nPlease delete your old instances if you no longer use them."
        #message = "########### ACCOUNT : " + accountName + " ###########\n" + message
    
        logger.debug ("Message: {0}".format(message))
        logger.info ("Send slack message...")
        result = sendSlackMessage(message)

        if result == 200:
            logger.info ("Slack notification sent.")
        else:
            logger.error ("Slack notification error, return code: %d" % (result))
    
def sendSlackMessage (message) :
    CONFIGFILE=  os.path.dirname(__file__) + "/lambda_config.ini"
    if not os.path.isfile(CONFIGFILE):
        logger.error("Config file not fount at '{0}'".format(CONFIGFILE))
        return False
    config = ConfigParser.ConfigParser()
    config.read(CONFIGFILE)
    try:
        SLACK_URL=config.get('slack', 'webhook_URL')
        SLACK_CHANNEL=config.get('slack', 'channel')
        SLACK_USERNAME=config.get('slack', 'username')
        SLACK_ICON = config.get('slack', 'icon_emoji')
        response = { "text" : message, "channel": SLACK_CHANNEL, "username": SLACK_USERNAME, "icon_emoji": SLACK_ICON}
        slack_response = requests.post(SLACK_URL,json=response, headers={'Content-Type': 'application/json'})
        return slack_response.status_code
    except Exception as inst:
        logger.error ("Slack Callout Failed.Message: '%s'" % (inst))
        return 0