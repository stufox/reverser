import requests
import random 


LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
MESSAGE_LENGTH=8
REQUESTID_LENGTH=8
ROUTER_CONNECT_TIMEOUT=3.05
ROUTER_READ_TIMEOUT=5

def random_string(length):
    return_string = []
    for x in range(length):
        random_letter=random.choice(LETTERS)
        return_string.append(random_letter)
    return ''.join(return_string)

def createServiceRequest():
    messageBody={}
    messageBody['RequestId']=random_string(REQUESTID_LENGTH)
    messageBody['Message']=random_string(MESSAGE_LENGTH)
    return messageBody

def send_request(uri):
    request = createServiceRequest()
    response = requests.post(uri,json=request, timeout=(ROUTER_CONNECT_TIMEOUT,ROUTER_READ_TIMEOUT))

def lambda_handler(event, context):
    uri = event['uri']
    for x in range(84):
        print(event)
