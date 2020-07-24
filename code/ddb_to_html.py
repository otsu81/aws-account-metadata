import boto3
import os
import logging
from dotenv import load_dotenv
from code.boto_factory import BotoFactory

load_dotenv()
logging.basicConfig(level=logging.WARNING)


class DDBToHTML():
    def __init__(self, session):
        self.ddb = BotoFactory().get_capability(
            boto3.client, session, 'dynamodb'
        )

    def table_to_list(self):
        paginator = self.ddb.get_paginator('scan')
        itr = paginator.paginate(
            TableName=os.environ['TABLE_NAME'],
            Select='ALL_ATTRIBUTES'
        )
        all_items = list()
        for i in itr:
            all_items = i['Items'] + all_items

        return all_items

    def get_all_attributes(self, list_ddb_items):
        """expects a list of dictionaries where each dictionary is a single item
        from DynamoDB"""
        attributes = set()
        for i in list_ddb_items:
            attributes = attributes.union(i.keys())
        return attributes

    def make_order_of_columns(self, attributes, desired_order_list):
        """takes input of attributes set and a partial or complete list of
        attributes in the desired order for the columns, e.g. should AccountId
        be first column
        then
            desired_order_list=['AccountId']
        If the desired order has fewer items than the attributes they will be
        added randomly depending on the order of the set returns list of order
        which can be used for HTML table generation
        """
        order_list = list()
        for attr in desired_order_list:
            try:
                attributes.remove(attr)
                order_list.append(attr)
            except Exception as e:
                raise(e)

        if len(attributes) > 0:
            for i in range(len(attributes)):
                order_list.append(attributes.pop())

        return order_list

    def make_table_head(self, ordered_list):
        thead = '<thead>\n\t\t\t<tr>\n'
        th_row = '\t\t\t\t<th>\n\t\t\t\t\t<p>%s\n\t\t\t\t</th>\n'
        for i in range(len(ordered_list)):
            thead += th_row % ordered_list[i]
        thead += '\t\t\t</tr>\n\t\t</thead>\n'
        return thead

    def make_table_row(self, ordered_list, account_info):
        tr = '\t\t<tr>\n'
        tr_td = "\t\t\t<td>\n\t\t\t\t<p>%s\n\t\t\t</td>\n"
        for i in range(len(ordered_list)):
            data = account_info.get(ordered_list[i])['S']
            if data.startswith('https://'):
                data = "<a href=\"%s\" target=_blank>%s</a>" % (data, data)
            tr += tr_td % data
        tr += '\t\t</tr>\n'
        return tr

    def make_html_file(self, column_order='', filename=''):
        if column_order == '':
            self.logging.warning('No column order specified')
            column_order = []
        if filename == '':
            filename = os.environ['DEFAULT_FILENAME']

        items = self.table_to_list()
        attributes = self.get_all_attributes(items)

        ordered_list = self.make_order_of_columns(
            attributes, column_order)

        thead = self.make_table_head(ordered_list)
        html_rows = str()
        for item in items:
            html_rows += self.make_table_row(ordered_list, item)

        params = {
            'TITLE': 'Account Roleswitching and Metadata',
            'THEAD_VALS': thead,
            'TR_VALS': html_rows
        }

        with open('html_templating/table_template.html', 'r') as f:
            template = f.read()

        path = filename
        with open(path, 'w') as out:
            out.write(
                template % params
            )
        return({'Status': 'OK', 'Path': path})
