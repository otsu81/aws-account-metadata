import os
import boto3
import logging
from dotenv import load_dotenv
from code.boto_factory import BotoFactory

load_dotenv()


class S3Ops():
    def __init__(self, session):
        self.session = session
        logging.basicConfig(level=logging.WARNING)

    def __get_client(self, rolename=''):
        if rolename == '':
            rolename = os.environ['DEFAULT_ROLE']
        return BotoFactory().get_capability(
            boto3.client, self.session, 's3', rolename=rolename
        )

    def put_html_file(self, local_path, bucket_name, bucket_object_name):
        s3 = self.__get_client()
        return s3.upload_file(
            local_path, bucket_name, bucket_object_name
        )

    def create_presigned_url(self, restricted_s3_rolename, bucket_name,
                             object_name, expiration=''):
        """Generate a presigned URL to share an S3 object
        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remainvalid
        :param restricted_s3_client: The S3 client used for generating the URL
        :return: Presigned URL as string. If error, returns None.
        The temporary credentials will have the same permissions as the S3
        client, if the client IAM credentials are not restricted tightly THIS
        CAN BE VERY DANGEROUS AND UNSECURE
        """
        restricted_s3_client = self.__get_client(
                rolename=restricted_s3_rolename
            )
        if expiration == '':
            expiration = 60
        try:
            response = restricted_s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': object_name
                    },
                ExpiresIn=expiration)
        except Exception as e:
            logging.error(e)
            return False
        # The response contains the presigned URL
        return response
