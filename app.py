import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import boto3
import constants
from s3 import s3Service
from ec2 import ec2_service
from sqsService import sqs_Service
import logging
import time
import s3

s3_inst = s3Service()
sqs_inst = sqs_Service()
ec2_inst = ec2_service()

logger = logging.getLogger(__name__)

app=Flask(__name__, template_folder='templates')

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Get current path
# path = os.getcwd()
# file Upload
# UPLOAD_FOLDER = os.path.join(path, 'uploads')

# Make directory if uploads is not exists
if not os.path.isdir('/home/ubuntu/flaskproject/uploads'):
    os.mkdir('/home/ubuntu/flaskproject/uploads')

app.config['UPLOAD_FOLDER'] = '/home/ubuntu/flaskproject/uploads'

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# s3_resource = boto3.resource('s3')
# s3_client = boto3.client('s3')
# sqs_resource = boto3.resource('sqs')
# sqs_client = boto3.client('sqs')
# ec2_resource = boto3.resource('ec2')
# send_queue_name = 'send_queue.fifo'
# receive_queue_name = 'receive_queue.fifo'
# session = boto3.session.Session()


# def create_bucket(bucket_name, s3_connection):
    
#     #current_region = session.region_name
    
#     s3_connection.create_bucket(
#         Bucket=bucket_name)
#         #CreateBucketConfiguration={
#         #'LocationConstraint': current_region})
#     #print(bucket_name, current_region)
#     return bucket_name

# def upload_file_to_s3(filepath, bucket_name, key):
#         try:
#             s3_resource.meta.client.upload_file(filepath, bucket_name, key)
#             logger.info("File has been uploaded successfully to %s",bucket_name)
#         except Exception as error:
#             logger.error("Error occurred while uploading file to s3 bucket %s", bucket_name)
#             raise error

# def send_message(messageBody, queue_name):
#         try:
#             queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
#         except Exception as error:
#             logger.warning("Queue doesnot exist %s", error)
#             # create_sqs(queue_name)
#             # queue = sqs_resource.get_queue_by_name(QueueName=queue_name)


#         response = queue.send_message(MessageBody=messageBody, MessageGroupId='string')
#         if 'Successful' in response:
#             for msg_meta in response['Successful']:
#                 '''logger.info(
#                     "Message sent: %s: %s",
#                     msg_meta['MessageId'],
#                     messages[int(msg_meta['Id'])]['body']
#                 )'''
#         if 'Failed' in response:
#             for msg_meta in response['Failed']:
#                 '''logger.warning(
#                     "Failed to send: %s: %s",
#                     msg_meta['MessageId'],
#                     messages[int(msg_meta['Id'])]['body']
#                 )'''
#         return response

# def create_sqs(queue_name):
#         try:
#             response = sqs_resource.create_queue(QueueName=queue_name, Attributes={'FifoQueue': 'true','ContentBasedDeduplication':'true'})
#             logger.warning("Queue has been created with url %s", response.url)
#         except Exception as error:
#             logger.exception("Couldn't create queue")
#             raise error
#         else:
#             return response

# def count_running_instances():
#         try:
#             instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
#             instances_list = [instance for instance in instances]
	    
#         except Exception as error:
#             logger.error("Error occured while counting number of instances")
#             raise error
#         return len(instances_list)

# def create_instance(image_id):
#         try:
#             ec2_resource.create_instances(ImageId=image_id, MinCount=1, MaxCount=1,
#                                  InstanceType='t2.micro')
#             logger.info("Instance created with imageId %s",image_id)
#         except Exception as error:
#             logger.warning("Error occurred while creating instance")
#             raise error

# def get_length_of_queue(queue_name):
#         try:
#             sqs_queue = sqs_resource.get_queue_by_name(QueueName = queue_name)
#             messages = sqs_queue.attributes["ApproximateNumberOfMessages"]
#         except Exception as error:
#             logger.warning("Error occurred while getting length of the queue!")
#             raise error
#         return int(messages)

# def receive_message(queue_name):
#         try:
#             queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
#             full_message = None
#             for message in queue.receive_messages(WaitTimeSeconds=20):
#                 full_message = message
#                 break
#         except Exception as error:
#             logger.exception("Unable to receive message from queue : %s", queue_name)
#             raise error
#         else:
#             return full_message

# def delete_message(queue_url, receipt_handle):
#         try:
#             sqs_client.delete_message(
#                 QueueUrl=queue_url,
#                 ReceiptHandle=receipt_handle
#             )
#             logger.info("Message %s has been deleted from the queue %s",receipt_handle,queue_url)
#         except Exception as error:
#             logger.exception()
#             raise error



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('update.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #bucket_name = create_bucket(bucket_name='cse546inputfile-nis', s3_connection=s3_resource.meta.client)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                s3_inst.upload_file_to_s3(file_path, constants.S3_INPUT_BUCKET, filename)
                s3.s3_resource.Object(constants.S3_INPUT_BUCKET, filename).upload_file(Filename=file_path)
                params = {'Bucket': constants.S3_INPUT_BUCKET, 'Key': filename}
                obj_url = s3.s3_client.generate_presigned_url('get_object', params)
                sqs_inst.send_message(obj_url, constants.INPUT_QUEUE_NAME)
        # flash('File(s) successfully uploaded')

        time.sleep(10)
        send_queue_len = sqs_inst.get_length_of_queue(constants.INPUT_QUEUE_NAME)
        print(send_queue_len)
        flash(str(send_queue_len) + ' File(s) successfully uploaded')
        flash('Classification Results: ')
        
        # autoscaling
        count_created_instances = 1
        while(count_created_instances < 20):
            if(count_created_instances < send_queue_len + 1):
                ec2_inst.create_instance('ami-0d8134fb9d44b9821', count_created_instances)
                count_created_instances += 1
                print(count_created_instances)
            else:
                break

        print("rec_length: ", sqs_inst.get_length_of_queue(constants.OUTPUT_QUEUE_NAME))
        #receive_queue = sqs_resource.get_queue_by_name(QueueName=receive_queue_name)
        
        while(sqs_inst.get_length_of_queue(constants.OUTPUT_QUEUE_NAME) < send_queue_len):
            time.sleep(5)
            print(sqs_inst.get_length_of_queue(constants.OUTPUT_QUEUE_NAME))
        
        
        out_str = ''
        count = 0
        while(count < send_queue_len):    
            message = sqs_inst.receive_message(constants.OUTPUT_QUEUE_NAME)
            receipt_handle = message.receipt_handle
            out_str += (message.body) + '\n'
            flash(message.body)
            sqs_inst.delete_message(message.queue_url, receipt_handle)
            count += 1

        
        outpufile = open('/home/ubuntu/flaskproject/outputfile.txt', "a+")
        outpufile.write(out_str)
        outpufile.close()
        s3_inst.upload_file_to_s3('/home/ubuntu/flaskproject/outputfile.txt', constants.S3_OUTPUT_BUCKET, 'outputfile.txt')
        #flash('File(s) successfully uploaded')


        return redirect('/')


if __name__ == "__main__":
    app.run()
