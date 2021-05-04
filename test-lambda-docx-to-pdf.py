import json
import boto3
import os
import base64

# --> Replace these values with yours <--
# Bucket name in S3
BUCKET_NAME = 'lambda-docx-to-pdf'
# 'Path' to file in S3 bucket. In my case I had a folder called 'input' with a file 'PacketFabricServiceOrderDiscountTemplate.docx' inside
INPUT_FILE_KEY = 'input/PacketFabricServiceOrderDiscountTemplate.docx'
# The ARN to the lambda function that executes `lambda-docx-to-pdf.py`
CONVERSION_LAMBDA_ARN = 'arn:aws:lambda:us-east-2:828009597444:function:docx-to-pdf'

# Note: If you want `lambda-docx-to-pdf.py` to upload the converted file to S3, uncomment
# the code for `s3_client.upload_file()` that's commented there, and replace the bucket name
# with yours'. Also create a folder called 'output' in the bucket, because it will
# put the converted files in that folder.

_, file_name = os.path.split(INPUT_FILE_KEY)

s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    
    s3_response = s3_client.get_object(Bucket=BUCKET_NAME, Key=INPUT_FILE_KEY)
    
    print("--> S3 RESPONSE: {}".format(s3_response))
    
    file_content = s3_response['Body'].read()
    # Encode in base64 to be JSON compatible
    file_content = base64.b64encode(file_content).decode('ascii')
    
    payload = json.dumps(
        {'file_name': file_name,
         'file_content': file_content}
    )
    
    response = lambda_client.invoke(
        FunctionName = CONVERSION_LAMBDA_ARN,
        InvocationType = 'RequestResponse',
        Payload = payload
    )
 
    responseFromChild = json.load(response['Payload'])
 
    return responseFromChild