from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json

SERVICE_VERSION = '2019-04-30'
API_KEY = 'SfSz3Tz8katbXZTLim4W50aKCBHOuR-RaJC-eNoyyZ8H'
URL = 'https://gateway.watsonplatform.net/discovery/api'
ENV_ID = 'b3e4ff43-07a6-46b8-b886-23108cff6904'


SUBMISSION_GROUP1_COL_ID = 'aaf80ee8-851d-40a6-9c83-6fdb9d819bbc'


def inst():

    authenticator = IAMAuthenticator(API_KEY)
    discovery = DiscoveryV1(version=SERVICE_VERSION,
                            authenticator=authenticator)
    discovery.set_service_url(URL)

    return discovery


def get_environments(discovery):
    environments = discovery.list_environments().get_result()
    print(json.dumps(environments, indent=2))

# def list_news_collections():
#     collections = discovery.list_collections(NEWS_ENV_ID).get_result()
#     news_collections = [x for x in collections['collections']]
#     print(json.dumps(collections, indent=2))

# , publication_date<=2018-02-15T00:00:00Z, publication_date>=2018-02-01T00:00:00Z
# enriched_text.keywords.text:"Theranos Inc"
# term='enriched_text.sentiment.document.label,count:3',
# return_fields=''


def upload_document(discovery, environment_id=None, collection_id=None, file_content=None, filename=None, file_content_type=None, metadata=None):
    #  handle nul env id

    if environment_id is None:
        print("Environment Id cannot be null")

    if collection_id is None:
        print("Collection Id cannot be null")

    if file_content is None:
        print("file_content cannot be null")

    if filename is None:
        print("filename cannot be null")

    # if file_content_type is None:
    #     print("file_content_type cannot be null")

    add_doc = discovery.add_document(
        environment_id,
        collection_id,
        file=file_content, filename=filename, file_content_type=file_content_type, metadata=metadata).get_result()

    print(json.dumps(add_doc, indent=2))

    return add_doc

def delete_document(discovery, environment_id=None, collection_id=None, document_id=None):
    #  handle nul env id

    if environment_id is None:
        print("Environment Id cannot be null")

    if collection_id is None:
        print("Collection Id cannot be null")

    # if file_content_type is None:
    #     print("file_content_type cannot be null")

    delete_doc = discovery.delete_document(
        environment_id,
        collection_id,
        document_id).get_result()

    print(json.dumps(delete_doc, indent=2))

    return delete_doc


def bulk_upload_document(discovery, environment_id=None, collection_id=None, document_list=None):
    print("document_list:{}".format(document_list))
    for doc in document_list:
        filename = doc["filename"]
        file_content = doc["file_content"]
        file_content_type = doc["file_content_type"]
        #  Add metadata also
        doc = upload_document(discovery, environment_id=environment_id, collection_id=collection_id,
                              file_content=file_content, filename=filename, file_content_type=file_content_type, metadata=None)
        print(json.dumps(doc, indent=2))


def get_results_by_doc_name(discovery, doc_name, return_fields_arr):

    all_results = []

    query_result = discovery.query(
        ENV_ID,
        SUBMISSION_GROUP1_COL_ID,
        query='extracted_metadata.filename:"' + doc_name + '"',
        return_fields=return_fields_arr,
        count='100')\
        .get_result()

    matching_results = query_result['matching_results']
    results = query_result["results"]

    with open('test.txt', 'w') as filehandle:
        filehandle.writelines("total_results:{} \n".format(matching_results))
        for item in results:

            if "submission_key" in item:
                new_key = item["submission_key"][0]
                # print("new_key::{}:{} ", new_key)
                new_value = ''
                if "submission_value" in item:
                    values = item["submission_value"]
                    for i in values:
                        new_value += "{}\n".format(i)

                filehandle.writelines("{}:{} \n".format(new_key, new_value))

            if "submission_data_elem" in item:
                submission_data_elem = item["submission_data_elem"][0]
                filehandle.writelines("{} \n".format(submission_data_elem))

    # json_result = json.dumps(query_results, indent=2)
    # print(json_result)
    # f = open("demofile.txt", "a")
    # f.write(json_result)


if __name__ == "__main__":

    wds = inst()

    delete_document(wds, "b3e4ff43-07a6-46b8-b886-23108cff6904","d16a19ec-46b5-42ed-a21b-d7e6a60f0f81","1d0d0285-1c00-454a-a4b8-20323f7c56ca")
    
    # get_results_by_doc_name("8ac98bff-0ca3-4b3c-a752-9c48eb8965c1_45156461_2018 Specifications (AmWINS).docx", [
    #                         "submission_key", "submission_value", "submission_data_elem"])
