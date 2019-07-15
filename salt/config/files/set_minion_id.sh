#!/bin/bash

sleep 60

export HOME="/home/ec2-user"

# Set minion_id
AWS_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_NAME=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$AWS_INSTANCE_ID" "Name=key,Values=Name" --output text | cut -f5)
if [ "$INSTANCE_NAME" != "" ]; then
  echo "$INSTANCE_NAME-$AWS_INSTANCE_ID" | sudo tee /etc/salt/minion_id
fi