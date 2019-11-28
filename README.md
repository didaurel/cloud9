<a href="https://drone.fpfis.eu/ec-europa/cloud9">
  <img src="https://drone.fpfis.eu/api/badges/ec-europa/cloud9/status.svg?branch=lambda/tagEC2InstancesAndVolumes" alt="build status">
</a>

# AWS Cloud9

Lambda scripts to manage cloud9 instances

## Instructions:


Python scripts 3.8 without dependances.

lambda_function.py: attach IAM roles to cloud9 instnaces.


## Developement

Script can be developed and tested on AWS Console > Lambda.


## Manual Deployement 

Create zip package:

```
pip2.7 install -r requirements.txt -t build
cp lambda_function.py ./build/
cd build
zip -r my_app.zip .
```

Upload zip to lambda function:
```
aws lambda update-function-code --function-name "MyLambdaFunctionName" --zip-file fileb://my_app.zip
```

