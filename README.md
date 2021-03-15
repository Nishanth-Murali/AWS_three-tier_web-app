# AWS_three-tier_web-app
three-tier web app to implement image recognition-as-a-service

Code:

The project uses three python programs that implement the different abstractions of the boto3 services, that have been used in the Flask app, which would run in the ‘app.py’ file. All the Three services are independent of each other and from the main module. They are loosely coupled such that they could be reused in other projects too with minimal or no changes. The three python modules using AWS SDKs in this project are;
1. SQSservice: ‘SQSservice’ contains methods that are required to perform basic operation on SQS Service like creating, deleting, sending, and receiving messages using ‘sqs’ resource of boto3 SDKs in Python.
2. S3Service: The boto3 SDKs also provide services to handle S3 buckets. ‘S3Service’ contains the methods that represent the Simple Storage Service (S3) at higher level client visibility. The methods help in uploading and downloading files to and from the S3 buckets.
3. EC2Service: ‘EC2Service’ contains methods that are required to perform basic operations on EC2, such as starting or terminating (stopping) an instance.

AMI codes:

1. Web-Tier Module
Web-tier Module consists of a Flask code ‘app.py’ which acts as driving functionality of the web-tier. In this module, we would be mapping the URI to the backend API through Flask. The Frontend HTML and Javascript are also mapped using the rendering template of the flask. The main function takes input from the user through the Html form which is built using the bootstrap library. The files are then sent to the S3 and its Object URL is generated. The generated File Urls are pushed into the SQS queue (Request queue) to be later read by app-tier instances. After pushing the input image url to the SQS, the Web-Tier polls for messages from the output queue (Response queue), which are then stored in the S3 bucket and displayed to the user using Jinja template.

2. App-Tier Module
For each input image, an app-tier Instance processes it to get the classification result using the ‘image_classification.py’ python code. It is the heart of the application as it takes care of delivering the output from the deep learning model to the user. The App-Tier Module First polls the message from the SQS, classifies the image using a deep learning model, and sends the output back to the web-tier through SQS. It also scales down the application, by shutting down the instance it runs on, after it sees no message in the Request queue.


3 Installation of the application:

1. Web-tier
We need to type in the following commands in the Ubuntu shell, before we can run the Flask app that would run on an Apache server. Before that, we should create a folder called ‘flaskproject’ in /home/ubuntu directory and add all the application files in this folder. The commands to be executed later are given below;
1. sudo apt-get update
2. sudo apt-get python3-pip
3. pip 3 install virtualenv
4. sudo apt-get install apache2 libapache2-mod-wsgi-py3
5. sudo ln -sT ~/flaskproject /var/www/html/flaskproject
6. sudo a2enmod wsgi
Then, we need to edit a configuration file whose path is /etc/apache2/sites-enabled/000-default.conf, wherein we will add the following lines after the line containing “var/www/html”;
WSGIDaemonProcess flaskproject threads=5
WSGIScriptAlias / /var/www/html/flaskproject/app.wsgi
<Directory flaskproject>
WSGIProcessGroup flaskproject
WSGIApplicationGroup %{GLOBAL}
Order deny,allow
Allow from all
</Directory>
Now, the environment for the Flask application is setup and we need to execute the below given three commands to run the application on EC2 instance’s localhost, so that we can type in the public DNS of the EC2 instance in our local browser to access the web-tier, i.e the frontend of our application.

2. App-tier

We need to have a folder named ‘classifier’ in /home/ubuntu of our app-instance EC2 and add the files ‘image_classification.py’ and ‘imagenet-labels.json’ in that folder. After this, we add the ‘pystart.sh’ shell script in /home/ubuntu and edit the crontab, in order to run the classification code automatically when the instance starts. The crontab can be edited by typing the commands;
1. crontab -e
2. @reboot /home/ubuntu/pystart.sh
With these configurations installed in the EC2 instance, we can build an AMI from this instance, so that we can create instances from this AMI, for autoscaling. All the app-instances created while auto-scaling the application will be using this AMI ID, so that all our configurations are up and running.
