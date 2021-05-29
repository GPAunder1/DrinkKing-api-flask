import boto3
from boto3.dynamodb.conditions import Key, Attr

class DynamoDB:
    def __init__(self):
        # Connect to DynamoDB and get ref to Table
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table_list = list(self.dynamodb.tables.all())
        table_name_list = [table.name for table in table_list ]
        if 'shops' not in table_name_list:
            self.create_table('shops')

    def create_table(self, table_name):
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'place_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'place_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        return table

    def insert_data(self, table_name, datas):
        table = self.dynamodb.Table(table_name)
        for data in datas:
            table.put_item(Item=data)

    def fetch_data(self, table_name, keyword):
        table = self.dynamodb.Table(table_name)

        response = table.scan(
            FilterExpression="contains (shopname, :shopnameVal)",
            ExpressionAttributeValues={":shopnameVal": keyword}
        )

        # return response['Items']
        return response['Items']
