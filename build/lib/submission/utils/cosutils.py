import re
import json
import ibm_boto3
from ibm_botocore.client import Config
# return object storage instance
from ibm_botocore.exceptions import ClientError


COS_API_KEY_ID = '25RdJDYL1Xlj0RvWGKRDCW7Xrn1esbA2yDtxyYGxOMym'
COS_RESOURCE_CRN = 'crn:v1:bluemix:public:cloud-object-storage:global:a/f45d02f7085c3cbf06ee8aeb2d38bcd4:ada9b6a7-33d5-43a5-aaa3-f876776a32f8::'
COS_AUTH_ENDPOINT = 'https://iam.ng.bluemix.net/oidc/token'
COS_ENDPOINT = 'https://s3.us-south.cloud-object-storage.appdomain.cloud'
BUCKET_NAME='riskanalyticsapp1'



def get_cos_resource():
    cos = ibm_boto3.resource("s3", ibm_api_key_id=COS_API_KEY_ID,
                            ibm_service_instance_id=COS_RESOURCE_CRN,
                            ibm_auth_endpoint=COS_AUTH_ENDPOINT,
                            config=Config(signature_version="oauth"),
                            endpoint_url=COS_ENDPOINT)
    return cos

def get_cos_client():
    cos_client = ibm_boto3.client('s3', ibm_api_key_id=COS_API_KEY_ID,
                             ibm_service_instance_id=COS_RESOURCE_CRN,
                             ibm_auth_endpoint=COS_AUTH_ENDPOINT,
                             config=Config(signature_version="oauth"),
                             endpoint_url=COS_ENDPOINT)
    return cos_client

def get_buckets():
    print("Retrieving list of buckets")
    try:
        cos = get_cos_resource()
        buckets = cos.buckets.all()
        for bucket in buckets:
            print("Bucket Name: {0}".format(bucket.name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve list buckets: {0}".format(e))


def get_filtered_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        cos = get_cos_resource()
        files = cos.Bucket(bucket_name).objects.all()
        filtered = filter(lambda file: re.match(r"^submission_documents_data.training.*pdf$",file.key), files) 
        filter_list = list(filtered)
        print("Total Items : {0} ".format(len(filter_list)))
        for file in filter_list:
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))

def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        cos = get_cos_resource()
        files = cos.Bucket(bucket_name).objects.all()        
        for file in files:
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))


def create_text_file(bucket_name, item_name, file_text):
    print("Creating new item: {0}".format(item_name))
    try:
        cos = get_cos_resource()
        cos.Object(bucket_name, item_name).put(
            Body=file_text
        )
        print("Item: {0} created!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create text file: {0}".format(e))

def get_bucket_contents(bucket_name, filter_regex):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        cos = get_cos_resource()
        keys = []
        files = cos.Bucket(bucket_name).objects.all()
        # print ("files:{}".format(files))
        filtered = filter(lambda file: re.match(filter_regex,file.key), files)        
        for file in filtered:
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
            keys.append(file.key)
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))

    return keys

def get_item(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(bucket_name, item_name))
    try:
        cos = get_cos_resource()
        file = cos.Object(bucket_name, item_name).get()

        # print("File Contents: {0}".format(file["Body"].read()))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
        return None
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))
        return None
    return file["Body"].read()


def save_file(bucket_name, item_name, file_content):
    print("Creating new item: {0}".format(item_name))
    try:
        cos = get_cos_resource()
        cos.Object(bucket_name, item_name).put(
            Body=file_content
        )
        print("Item: {0} created!".format(item_name))
        return "SUCCESS"
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
        return "FAILURE"
    except Exception as e:
        print("Unable to create text file: {0}".format(e))
        return "FAILURE"

def delete_all_files(bucket_name):
    print("Deleting files from : {0}".format(bucket_name))
    try:
        cos = get_cos_resource()
        files = cos.Bucket(bucket_name).objects.all()
        filtered = filter(lambda file: re.match(r"^submission_documents_data/training",file.key), files)  
        object_dict = dict()
        
        key_list = []
        for file in filtered:
            # print("Item: {0} ({1} bytes).".format(file.key, file.size))
            key_dict = dict()
            key = file.key
            key_dict["Key"] = key
            key_list.append(key_dict)

        object_dict["Objects"] = key_list

        # print(object_dict)
        cos_client = get_cos_client()
        response = cos_client.delete_objects(
            Bucket=bucket_name,
            Delete=object_dict
        )

        print("Deleted items for {0}\n".format(bucket_name))
        print(json.dumps(response.get("Deleted"), indent=4))

    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))

if __name__ == "__main__":
  
    # delete_all_files ("everest-submission-bucket")
    get_filtered_bucket_contents("everest-submission-bucket")
    # get_buckets()

    # get_bucket_contents("cos-everest-submission-data", r"^email_message_data.*msg$")

    # create_text_file(BUCKET_NAME, 'abc/test.txt', 'Some content')

    # get_bucket_contents(BUCKET_NAME)

    # get_item(BUCKET_NAME, 'abc/test.txt')
