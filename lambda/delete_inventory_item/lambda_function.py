import boto3
import json

def lambda_handler(event, context):
    dynamo_client = boto3.client('dynamodb')
    table_name = 'Inventory'

    # Validate input
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    id_value = event['pathParameters']['id']

    try:
        # 1. Query all items with the given id
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
                'body': json.dumps("No items found for this id")
            }

        # 2. Delete each item using FULL primary key
        deleted_count = 0

        for item in items:
            dynamo_client.delete_item(
                TableName=table_name,
                Key={
                    'id': item['id'],
                    'location_id': item['location_id']
                }
            )
            deleted_count += 1

        return {
            'statusCode': 200,
            'body': json.dumps(f"Deleted {deleted_count} item(s) for id {id_value}")
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }