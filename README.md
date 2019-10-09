<a href="https://drone.fpfis.eu/ec-europa/cloud9">
  <img src="https://drone.fpfis.eu/api/badges/ec-europa/cloud9/status.svg?branch=lambda/tagEC2InstancesAndVolumes" alt="build status">
</a>

# AWS Cloud9

Lambda scripts to manage cloud9 instances

## Instructions:


Python scripts 3.7 without dependances.

lambda_function.py: Delete all sopped packer instance (tag:Name:packer-build* & instance-state-name:stopped)


## Developement

Script can be developed and tested on AWS Console > Lambda.


## Manual Deployement 

Create zip package:

```
pip install -r requirements.txt -t build
cp lambda_function.py ./build/
cd build
zip -r my_app.zip .
```

Upload zip to lambda function:
```
aws lambda update-function-code --function-name "deletePackerEC2" --zip-file fileb://my_app.zip
```

