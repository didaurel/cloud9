
ZIP_FILE="my_app.zip"

function printAvailableLambdaFunction {
    functions_list=$(aws lambda list-functions --output json | grep FunctionName | cut -d ":" -f2)
    echo "Available functions:" $functions_list
}

lambdaFunctionName=$1
if [ "$lambdaFunctionName" = "" ] ; then
    echo "ERROR: mising arg1 (lambdaFunctionName)"
    printAvailableLambdaFunction
    exit 11
fi

if [ ! -f $ZIP_FILE ] ; then
  echo "ERROR: zip file not found at '$ZIP_FILE'"
  exit 12
fi

aws lambda update-function-code --function-name "$lambdaFunctionName" --zip-file fileb://$ZIP_FILE

if [ "$?" != "0" ];then
  echo "ERROR, ensure the lambda function '$lambdaFunctionName' exist."
  printAvailableLambdaFunction
  exit 13
fi
