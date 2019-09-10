#!/bin/bash

export HOME="/home/ec2-user"

# Load Credentials for Cloud9Role
aws configure set region eu-west-1 --profile Cloud9Role
aws sts assume-role --role-arn "arn:aws:iam::469132580751:role/Cloud9Role" --role-session-name Cloud9Role --profile Cloud9Role --duration-seconds 900 > /dev/null

# Set minion_id
AWS_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_NAME=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$AWS_INSTANCE_ID" "Name=key,Values=Name" --profile Cloud9Role --output text | cut -f5)
if [ "$INSTANCE_NAME" != "" ]; then
  echo "$INSTANCE_NAME-$AWS_INSTANCE_ID" | sudo tee /etc/salt/minion_id
fi