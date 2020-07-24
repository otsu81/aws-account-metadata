import boto3
from botocore.exceptions import ClientError
import logging
from code.boto_factory import BotoFactory


class AccountOps:
    def get_accounts(self, session):

        org = BotoFactory().get_capability(
            boto3.client, session, 'organizations'
        )
        accounts = dict()
        paginator = org.get_paginator('list_accounts')
        itr = paginator.paginate()
        for i in itr:
            for account in i['Accounts']:
                accounts[account['Id']] = account

        return accounts

    def check_account_for_roles(self, session, account_id, roles):
        for r in roles:
            try:
                BotoFactory().get_capability(
                    boto3.client, session, 'sts', account_id,
                    rolename=r
                )
                roles[r] = True
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logging.info(f"{r} did not exist in {account_id}")
                    pass
        return roles

    def check_acount_for_billing_access(self, session, account_id):
        costexplorer = BotoFactory().get_capability(
            boto3.client, session, 'ce', account_id=account_id
        )
        response = costexplorer.get_cost_and_usage(
            TimePeriod={
                'Start': '2019-08-01',
                'End': '2019-09-01'
            },
            Granularity='MONTHLY',
            Metrics=[
                'BlendedCost'
            ]
        )
        return response
