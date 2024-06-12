import json
import csv
import urllib.parse
import boto3
import os

s3 = boto3.client('s3')
sns_client = boto3.client('sns')
TOPIC_ARN = os.environ['TOPIC_ARN']

def lambda_handler(event, context):
    # Extract bucket, key, and event name from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    eventname = event['Records'][0]['eventName']
    sns_message = (
        f"this is my lambda function for testing\n\n"
        f"BUCKET NAME: {bucket}\n\n"
        f"FILE NAME: {key}\n\n"
        f"OPERATION: {eventname}\n\n"
    )
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        body = response['Body'].read()
        csv_content = body.decode('utf-8').splitlines()
        csv_reader = csv.reader(csv_content)
        csv_data = [row for row in csv_reader]
        csv_string = '\n'.join([','.join(row) for row in csv_data])
        sns_message += (
            f"FILE CONTENT TYPE: {content_type}\n\n"
            f"FILE CONTENT:\n{csv_string}"
        )
        subject = f"S3 Bucket[{bucket}] Event[{eventname}]"
        sns_response = sns_client.publish(
            TargetArn=TOPIC_ARN,
            Message=sns_message,
            Subject=subject
        )
        return content_type

    except Exception as e:
        print(e)
        print(
            f'Error getting object {key} from bucket {bucket}. '
            f'Make sure they exist and your bucket is in the same region as this function.'
        )
        raise e
