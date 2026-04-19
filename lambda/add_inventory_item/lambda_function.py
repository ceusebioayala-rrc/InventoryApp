"""This is a lambda function for adding inventory items to DynamoDB.

Testing
"""

import json
import uuid

import boto3


def lambda_handler(event, _context):
    """Handles request to add inventory items."""
    
    # Parse incoming JSON data
    try:
        data = json.loads(event['body'])
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps("Bad request. Please provide the data.")
        }

    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')

    # Generate a unique ID
    unique_id = str(uuid.uuid4())

    # Insert data into DynamoDB
    try:
        table.put_item(
            Item={
                'id': unique_id,
                'location_id': data['location_id'],
                'name': data['name'],
                'description': data['description'],
                'qty': data['qty'],
                'price': data['price']
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with ID {unique_id} added successfully.")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error adding item: {str(e)}")
        }