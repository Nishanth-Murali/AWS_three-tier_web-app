import os
import boto3
import constants
from s3 import s3Service
from ec2 import ec2_service
from sqsService import sqs_Service
import logging
import time
import s3
import re
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import json
import sys
import numpy as np
import requests

s3_inst = s3Service()
sqs_inst = sqs_Service()
ec2_inst = ec2_service()

def predict_label(file_url): #file-path
    url = str(file_url)
    img = Image.open(requests.get(url, stream=True).raw)
    model = models.resnet18(pretrained=True)

    model.eval()
    img_tensor = transforms.ToTensor()(img).unsqueeze_(0)
    outputs = model(img_tensor)
    _, predicted = torch.max(outputs.data, 1)

    with open('./imagenet-labels.json') as f:
        labels = json.load(f)
    result = labels[np.array(predicted)[0]]
    return result


def run_listener_dispatcher():
    while(True):
        message = sqs_inst.receive_message(constants.INPUT_QUEUE_NAME)
        if(message==None):
            time.sleep(10)
            continue
        else:
            try:
                input_url = message.body
                receipt_handle = message.receipt_handle
                output = predict_label(input_url)
                key_match = re.search(".com/(.*)\?", input_url)
                key = key_match.group(1)
                # s3_inst.create_bucket(constants.S3_OUTPUT_BUCKET)
                s3_inst.read_file(constants.S3_OUTPUT_BUCKET, constants.OUTPUT_FILE, ".\\" + constants.OUTPUT_FILE)
                outpufile = open("./" + constants.OUTPUT_FILE, "a+")
                # print(key, output)
                outpufile.write(key + ',' + output + '\n')
                outpufile.close()
                s3_inst.upload_file_to_s3("./" + constants.OUTPUT_FILE, constants.S3_OUTPUT_BUCKET,
                                         constants.OUTPUT_FILE)
                outpufile.close()
                sqs_inst.delete_message(message.queue_url, receipt_handle)
                sqs_inst.send_message(key + ',' + output, constants.OUTPUT_QUEUE_NAME)
            except Exception as error:
                raise error


if __name__ == '__main__':
    run_listener_dispatcher()
