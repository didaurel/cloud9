import boto3
import datetime
import os
import requests

START_DATE = 180

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
iam = boto3.client('iam')

def lambda_handler(event, context):
  i=0

  global START_DATE
  if "START_DATE" in event:
      START_DATE = event["START_DATE"]

  start_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=START_DATE)
  logger.info ("Check user not connected since " + start_date.strftime("%A %d. %B %Y"))
  message = []
  paginator = iam.get_paginator('list_users')
  for page in paginator.paginate():
    for user in page['Users']:
      if user['UserName'] != "drone-lambda-cd":
        if "PasswordLastUsed" in user:
          if user['PasswordLastUsed'] < start_date:
            mess="{} User {} not connected to AWS console since {}".format(chr(8226), user['UserName'], user['PasswordLastUsed'].strftime("%Y-%m-%d"))
            message.append(mess)
            logger.debug (mess)
            i=i+1
        else:
          mess="{} User {} never connected to AWS console".format(chr(8226), user['UserName'])
          message.append(mess)
          logger.debug (mess)
          i=i+1

  logger.info ("{} users found.".format(i))
  if i != 0:
    message = ["There are {} users with no recent activity on account digit-d1-nexteuropa-dev of AWS console:".format(i), *message]
    logger.info ("Send slack message...")

    result = sendSlackMessage('\n'.join(message))

    if result == 200:
        logger.info ("Slack notification sent.")
    else:
        logger.error ("Slack notification error, return code: %d" % (result))

def sendSlackMessage (message) :
    try:
        SLACK_URL=os.environ['webhook_URL']
        SLACK_CHANNEL=os.environ['channel']
        SLACK_USERNAME=os.environ['username']
        SLACK_ICON=os.environ['icon_emoji']
        response = { "text" : message, "channel": SLACK_CHANNEL, "username": SLACK_USERNAME, "icon_emoji": SLACK_ICON}
        slack_response = requests.post(SLACK_URL,json=response, headers={'Content-Type': 'application/json'})
        return slack_response.status_code
    except Exception as inst:
        logger.error ("Slack Callout Failed.Message: '%s'" % (inst))
        return 0