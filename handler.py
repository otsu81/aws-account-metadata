import boto3
import json
import logging
import os
from dotenv import load_dotenv
from code.boto_factory import BotoFactory
from code.ddb_ops import DynamoDBOps
from code.account_ops import AccountOps
from code.ddb_to_html import DDBToHTML
from code.s3_ops import S3Ops

load_dotenv()
logging.basicConfig(level=logging.WARNING)


def __make_roleswitch_url(account):
    return ("https://signin.aws.amazon.com/switchrole?account=" +
            account['Id'] +
            "&roleName=" +
            os.environ['DEFAULT_ROLE'] +
            "&displayName=" +
            account['Name'])


def main(event, context):
    """ Updates the metadata DynamoDB table with Organizations as source of truth,
    Must have an existing table to run (from .env)
    If there is no table, run make_table.py
    """
    if event.get('profile_name'):
        session = boto3.Session(profile_name=event.get('profile_name'))
    else:
        session = boto3.Session()

    # check if DDB table exists, if not create it
    ddb_r = BotoFactory().get_capability(
        boto3.resource, session, 'dynamodb'
    )
    table = ddb_r.Table(os.environ['TABLE_NAME'])

    try:
        table.creation_date_time
    except ddb_r.meta.client.exceptions.ResourceNotFoundException:
        logging.error('Table does not exist, creating')
        logging.info(DynamoDBOps().make_metadata_table(
            ddb_r.meta.client, os.environ['TABLE_NAME']
        ))
        table.wait_until_exists()
        logging.info(f"Table created: {table.creation_date_time}")

    # create dictionary of all ACTIVE organization accounts
    accounts = AccountOps().get_accounts(session)

    ddb = BotoFactory().get_capability(
        boto3.client, session, 'dynamodb'
    )
    # update dynamoDB with account information
    DynamoDBOps().populate_baseline_metadata(
        ddb, os.environ['TABLE_NAME'], accounts
    )

    # make roleswitch URLs
    for id in accounts:
        DynamoDBOps().add_roleswitch_url(
            ddb, os.environ['TABLE_NAME'], id,
            __make_roleswitch_url(accounts[id]))

    # make HTML file
    column_order = [
        'AccountId',
        'Name',
        'RoleSwitchURL'
    ]
    local_path = f"/tmp/{os.environ['DEFAULT_FILENAME']}"
    logging.info(
        DDBToHTML(session).make_html_file(
            column_order=column_order,
            filename=local_path
            )
        )

    # put in S3, get pre-signed URL
    object_name = 'metadata.html'
    S3Ops(session).put_html_file(
        local_path, os.environ['HTML_BUCKET'], object_name
    )
    url = S3Ops(session).create_presigned_url(
        os.environ['S3_READONLY_ROLE'],
        os.environ['HTML_BUCKET'],
        object_name
    )

    response = {
        'success': True,
        'url': url
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }