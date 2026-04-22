"""Lambda function for getting inventory items by location_id from DynamoDB."""

import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = 'Inventory'
GSI_NAME = 'GSI_LOCATIONID_ID'

# Convert Decimal to int/float for JSON serialization
def convert_decimals(obj):
    """Convert Decimal to int/float for JSON serialization."""

    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

def lambda_handler(event, _context):
    """Handles request to get inventory items by location_id."""

    table = dynamodb.Table(TABLE_NAME)

    # Validate path parameter
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    # Map API param → DynamoDB attribute
    location_id = event['pathParameters']['id']

    try:
        location_id = int(location_id)

        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key('location_id').eq(location_id)
        )

        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('No items found for this location')
            }

        # Convert Decimal values
        items = convert_decimals(items)

        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }

    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"DynamoDB error: {error_message}")

        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}")

        return {
            'statusCode': 500,
            'body': json.dumps("Internal server error")
        }