import boto3,sys,logging
import constants

logger = logging.getLogger(__name__)
sqs_resource = boto3.resource("sqs", constants.AWS_REGION, aws_access_key_id=constants.AWS_ACCESS_KEY, aws_secret_access_key=constants.AWS_SECRET_ACCESS_ID)
sqs_client = boto3.client("sqs", constants.AWS_REGION, aws_access_key_id=constants.AWS_ACCESS_KEY, aws_secret_access_key=constants.AWS_SECRET_ACCESS_ID)

class sqs_Service:
    def create_sqs(self, queue_name):
        try:
            response = sqs_resource.create_queue(QueueName=queue_name, Attributes={'FifoQueue': 'true','ContentBasedDeduplication':'true'})
            logger.warning("Queue has been created with url %s", response.url)
        except Exception as error:
            logger.exception("Couldn't create queue")
            raise error
        else:
            return response

    '''def get_queue(self, queue_name):
        try:
            logger.info("Queue Url for %s is %s", queue_url, queue_name)
        except ClientError as error:
            logger.warning("unable to get Queue Url for queue name %s")
            raise error
        else:
            return queue'''

    def get_length_of_queue(self, queue_name):
        try:
            sqs_queue = sqs_resource.get_queue_by_name(QueueName = queue_name)
            messages = sqs_queue.attributes["ApproximateNumberOfMessages"]
        except Exception as error:
            logger.warning("Error occurred while getting length of the queue!")
            raise error
        return int(messages)

    def send_message(self, messageBody, queue_name):
        try:
            queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
        except Exception as error:
            logger.warning("Queue doesnot exist %s", error)
            # sqsService.create_sqs(queue_name)
            # queue = sqs_resource.get_queue_by_name(QueueName=queue_name)


        response = queue.send_message(MessageBody=messageBody, MessageGroupId='string')
        '''if 'Successful' in response:
            for msg_meta in response['Successful']:
                logger.info(
                    "Message sent: %s: %s",
                    msg_meta['MessageId'],
                    messages[int(msg_meta['Id'])]['body']
                )
        if 'Failed' in response:
            for msg_meta in response['Failed']:
                logger.warning(
                    "Failed to send: %s: %s",
                    msg_meta['MessageId'],
                    messages[int(msg_meta['Id'])]['body']
                )'''
        return response


    def receive_message(self, queue_name):
        try:
            queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
            full_message = None
            for message in queue.receive_messages(WaitTimeSeconds=20):
                full_message = message
                break
        except Exception as error:
            logger.exception("Unable to receive message from queue : %s", queue_name)
            raise error
        else:
            return full_message


    def delete_message(self, queue_url,receipt_handle):
        try:
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.info("Message %s has been deleted from the queue %s",receipt_handle,queue_url)
        except Exception as error:
            logger.exception()
            raise error
