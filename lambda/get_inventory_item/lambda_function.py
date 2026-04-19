import json

import boto3


def lambda_handler(event, context):
    dynamo_client = boto3.client('dynamodb')
    table_name = 'Inventory'

    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    id_value = event['pathParameters']['id']

    try:
        response = dynamo_client.query(
            TableName=table_name,
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': {'S': id_value}
            }
        )

        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('No items found')
            }

        return {
            'statusCode': 200,
            'body': json.dumps(items, default=str)
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }