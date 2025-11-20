import json
import os

def lambda_handler(event, context):
    s3_bucket = os.environ.get('S3_BUCKET', 'default-bucket')
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from Lambda!',
            'bucket': s3_bucket
        })
    }
