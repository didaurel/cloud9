<a href="https://drone.fpfis.eu/ec-europa/cloud9">
  <img src="https://drone.fpfis.eu/api/badges/ec-europa/cloud9/status.svg?branch=lambda/resizeEC2Volume" alt="build status">
</a>

# AWS Cloud9

Lambda scripts to manage cloud9 instances

## Instructions:


Python scripts 3.8 with request dependances.

lambdaFunction.py: Send slack notification for EC2 cloud9 instances started more than 8 hours.

Script triggered by [CloudWatch Event](cloudWatch.Event)

## Developement

Script can be developed and tested on AWS Console > Lambda.


## Deployement 

Script can be deployed on AWS Console > Lambda or using AWS CLI:
```
zip -r my_app.zip lambda_function.py
aws lambda update-function-code --function-name "MyLambdaFunctionName" --zip-file fileb://my_app.zip
```

Using scripts:
```
# Create package
./lambdaPackageCreate.sh
# Upload package
./lambdaPackageUpload.sh resizeEC2Volume
```
