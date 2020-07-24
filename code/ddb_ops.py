import json
import logging


class DynamoDBOps:

    def make_metadata_table(self, ddb_client, tablename, ddb_config=''):
        if ddb_config == '':
            ddb_config = {
                'TableName': tablename,
                'KeySchema': [
                    {
                        'AttributeName': 'AccountId',
                        'KeyType': 'HASH'
                    }
                ],
                'AttributeDefinitions': [
                    {
                        'AttributeName': 'AccountId',
                        'AttributeType': 'S'
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            }

        return ddb_client.create_table(**ddb_config)

    def populate_baseline_metadata(self, ddb_client, tablename, accounts):
        for account in accounts:
            response = ddb_client.update_item(
                TableName=tablename,
                Key={
                    'AccountId': {
                        'S': account
                    }
                },
                ExpressionAttributeNames={
                    '#St': 'Status',
                    '#N': 'Name',
                    '#Em': 'Email'
                },
                ExpressionAttributeValues={
                    ':st': {
                        'S': accounts[account]['Status']
                    },
                    ':n': {
                        'S': accounts[account]['Name']
                    },
                    ':em': {
                        'S': accounts[account]['Email']
                    }
                },
                UpdateExpression='SET #St = :st, #N = :n, #Em = :em',
                ReturnValues='ALL_NEW'
            )
        logging.info(json.dumps(response, indent=4, default=str))

    def make_ddb_bool_dict(self, input_dict):
        ddb_bool_dict = dict()
        for attr in input_dict:
            ddb_bool_dict[attr] = {'BOOL': input_dict[attr]}
        return ddb_bool_dict

    def add_roleswitch_url(self, ddb_client, table, account_id, url):
        response = ddb_client.update_item(
            TableName=table,
            Key={
                'AccountId': {
                    'S': account_id
                }
            },
            ExpressionAttributeValues={
                ':url': {'S': url},
            },
            UpdateExpression='SET RoleSwitchURL = :url',
            ReturnValues='ALL_NEW'
        )
        return response
