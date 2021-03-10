import boto3,sys,logging
import constants
import uuid

logger = logging.getLogger(__name__)
s3_resource = boto3.resource("s3", constants.AWS_REGION, aws_access_key_id=constants.AWS_ACCESS_KEY, aws_secret_access_key=constants.AWS_SECRET_ACCESS_ID)
s3_client = boto3.client("s3", constants.AWS_REGION, aws_access_key_id=constants.AWS_ACCESS_KEY, aws_secret_access_key=constants.AWS_SECRET_ACCESS_ID)

class s3Service:
    def create_bucket_name(self, bucket_prefix):
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])


    def create_bucket(self, bucket_name):
        try:
            bucket = s3_resource.create_bucket(Bucket=bucket_name)
            logger.info("Bucket has been created with name %s", constants.S3_BUCKET_NAME)
        except Exception as error:
            logger.error("Error occurred while creating the bucket %s", constants.S3_BUCKET_NAME)
            raise error

    def get_bucket(self, bucket_name):
        try:
            response = s3_resource.Bucket(bucket_name)
            return response
        except Exception as error:
            logger.error("Error occurred while trying to access the bucket")
            raise error
        return None

    def upload_file_to_s3(self, filepath, bucket_name, key):
        try:
            s3_resource.meta.client.upload_file(filepath, bucket_name, key)
            logger.info("File has been uploaded successfully to %s",bucket_name)
        except Exception as error:
            logger.error("Error occurred while uploading file to s3 bucket %s", bucket_name)
            raise error

    def read_file(self, bucket_name, key, path_to_download):
        print(path_to_download)
        try:
            s3_object = s3_resource.Object(bucket_name, key)
            s3_object.download_file(path_to_download)
        except Exception as error:
            logger.error("error occurred while trying to fetch the file %s",error)




