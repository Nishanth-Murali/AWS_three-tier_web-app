import boto3,sys,logging
import requests
import constants

logger = logging.getLogger(__name__)
ec2_resource = boto3.resource("ec2", constants.AWS_REGION, aws_access_key_id=constants.AWS_ACCESS_KEY, aws_secret_access_key=constants.AWS_SECRET_ACCESS_ID)

class ec2_service:
    def create_instance(self, image_id):
        try:
            ec2_resource.create_instances(ImageId=image_id, MinCount=1, MaxCount=1,
                                 InstanceType='t2.micro')
            logger.info("Instance created with imageId %s",image_id)
        except Exception as error:
            logger.warning("Error occurred while creating instance")
            raise error

    def stop_instance(self):
        try:
            response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
            instance_id = response.text
            print(instance_id)
            ec2_resource.instances.filter(InstanceIds=[instance_id]).stop()
        except Exception as error:
            raise error

    def terminate_instance(self, instance_id):
        try:
            # instance_id2 = ec2_metadata.instance_id
            response = ec2_resource.instances.filter(InstanceIds=[instance_id]).terminate()
            print(response)
        except Exception as error:
            raise error

    def count_instances(self):
        try:
            instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            instances_list = [instance for instance in instances]
            return len(instances_list)
        except Exception as error:
            logger.error("Error occured while counting number of instances")
            raise error
        return 0

    def get_stopped_instanceId(self):
        try:
            for instance in ec2_resource.instances.all():
                if(instance.state['Name']=='stopped'):
                    return instance.id
        except Exception as error:
            raise error
        return None

    def start_instance(self, instance_id):
        try:
            # instance_id2 = ec2_metadata.instance_id
            response = ec2_resource.instances.filter(InstanceIds=[instance_id]).start()
            print(response)
        except Exception as error:
            raise error


