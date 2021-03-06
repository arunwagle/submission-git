import logging
import os
from os import walk
import shutil
import glob
import json
import convertapi
import ibm_db
import ibm_db_dbi
# importing the requests library
import requests
import base64
import time
from urllib.parse import quote
from submission.utils import cosutils, db2utils

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)

# api-endpoint
CONVERT_IO_URL = "https://api.convertio.co/convert"
convertio_api_key = '92aa5b192c0981506a44a2c094af8cd9'
OBJECT_STORAGE_PUBLIC_URL = "https://everest-submission-bucket.s3.us-south.cloud-object-storage.appdomain.cloud"


def main(params):
    logging.info('Calling fn_doc_converto_txt.')

    try:

        cos_everest_submission_bucket = params.get(
            "cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")

        submission_id = params.get("submission_id", None)
        if submission_id is None or "":
            raise Exception("Pass submission_id")

        submissions_data_folder = params.get("submissions_data_folder", None)
        if submissions_data_folder is None or "":
            raise Exception("Pass submissions_data_folder")

        mode = params.get("mode", None)
        if mode is None or "":
            raise Exception("Pass mode")

        final_pdf_object_storage_key = submissions_data_folder + "/" + \
            mode + "/" + str(submission_id) + "/"
            # + "/final_pdf_split"
        
        final_txt_object_storage_key_prefix = submissions_data_folder + \
            "/" + mode + "/" + str(submission_id) 


        regex = r"^" + final_pdf_object_storage_key + ".*(?i)(pdf|htm).*$"

        file_keys = cosutils.get_bucket_contents(
            cos_everest_submission_bucket, regex)

        extensions = ['.pdf', '.html', '.htm']

        for key in file_keys:
            print ("key:{}".format(key))
            if key.lower().endswith(tuple(extensions)):
                file_name = os.path.basename(key)
                file_name_without_ext, file_extension = os.path.splitext(
                    file_name)

                print("file_extension::", file_extension)
                print("is final_pdf_split::", "final_pdf_split" not in key)
                
                if file_extension.lower() in (".pdf")  and "final_pdf_split" not in key :
                    print("Continue for loop")
                    continue

                url = OBJECT_STORAGE_PUBLIC_URL + "/" + \
                    quote(key)
                PARAMS = {"apikey": convertio_api_key,
                    "input": "url", "file": url, "outputformat": "txt"}

                print(url)

                db_conn = db2utils.get_connection()
                print("db_conn: {}".format(db_conn))
                sql = f'''SELECT EVRE_LEARNING_EMAIL_ATTACHMENTS_ID FROM EVERESTSCHEMA.EVRE_LEARNING_SPLIT_CONTENT 
                where  EVRE_EMAIL_MSG_ID={submission_id} and DOCUMENT_NAME='{key}' and DOCUMENT_TYPE='{file_extension}' '''
                print("sql: {}".format(sql))

                stmt = ibm_db.exec_immediate(db_conn, sql)
                
                result = ibm_db.fetch_both(stmt)
                pdf_id = None
                if result:
                    pdf_id = result["EVRE_LEARNING_EMAIL_ATTACHMENTS_ID"]
                else:
                    sql = f'''SELECT ID FROM EVERESTSCHEMA.evre_learning_email_attachments 
                    where  EVRE_EMAIL_MSG_ID={submission_id} and DOCUMENT_NAME='{key}' and DOCUMENT_TYPE='{file_extension}' '''
                    print("sql: {}".format(sql))

                    stmt = ibm_db.exec_immediate(db_conn, sql)
                    result = ibm_db.fetch_both(stmt)
                    if result:
                        pdf_id = result["ID"]
                    else:
                        raise Exception("pdf_id is not present. Check the data")


                # sending get request and saving the response as response object
                r = requests.post(url=CONVERT_IO_URL,
                                  data=json.dumps(PARAMS)   )

                return_val = json.loads(r.text)
                print("1......return_val::{}", return_val)

                status = return_val["status"]
                code = return_val["code"]

                if code == 200 and status == "ok":
                    id = return_val["data"]["id"]
                    print("converted document id::", id)
                    check_status_url = CONVERT_IO_URL + "/" + id + "/status"
                    print("check_status_url::", check_status_url)
                    while True:
                        r = requests.get(url=check_status_url, stream=True)
                        return_val = json.loads(r.text)
                        print("2.......status::return_val::", return_val)
                        status = return_val["status"]
                        code = return_val["code"]
                        if code == 200 and status == "ok":
                            step = return_val["data"]["step"]
                            step_percent = return_val["data"]["step_percent"]
                            if step == "finish" and step_percent == 100:
                                id = return_val["data"]["id"]
                                print(
                                    "Get content, store in object storage and update db2 and exist")

                                # get content
                                get_result_url = CONVERT_IO_URL + "/" + id + "/dl/base64"
                                print("status::get_result_url::", get_result_url)
                                # , stream=True
                                r = requests.get(url=get_result_url, stream=True)
                                return_val = json.loads(r.text)

                                status = return_val["status"]
                                code = return_val["code"]
                                if code == 200 and status == "ok":
                                    content = return_val["data"]["content"]

                                    txt_object_storage_key = final_txt_object_storage_key_prefix + \
                                        "/" + "standardized_txt_dir" + "/" + file_name_without_ext + ".txt"
                                    print("cos_everest_submission_bucket: {}: txt_object_storage_key: {} ".format(
                                        cos_everest_submission_bucket, txt_object_storage_key))

                                    # Write attachments to the object storage
                                    return_val = cosutils.save_file(
                                        cos_everest_submission_bucket, txt_object_storage_key, base64.b64decode(content))

                                    db_conn = db2utils.get_connection()
                                    print("db_conn: {}".format(db_conn))
                                    sql = f'''SELECT ID FROM FINAL TABLE (INSERT INTO EVERESTSCHEMA.EVRE_LEARNING_SPLIT_CONTENT (EVRE_EMAIL_MSG_ID, EVRE_LEARNING_EMAIL_ATTACHMENTS_ID,
                                                DOCUMENT_NAME, DOCUMENT_TYPE, CLASSIFICATION_TYPE, STATUS, USED_FOR, DESCRIPTION)
                                                VALUES ({submission_id},
                                                    {pdf_id},
                                                    '{txt_object_storage_key}',
                                                    '.txt',
                                                    'N/A',
                                                    'N',
                                                    'RUNTIME',
                                                    'APPLY_NLP')
                                                )
                                                '''
                                    print("sql: {}".format(sql))

                                    stmt = ibm_db.exec_immediate(db_conn, sql)
                                    result = ibm_db.fetch_both(stmt)
                                    attachment_id = None
                                    if result:
                                        attachment_id = result["ID"]

                                break
                            else:
                                time.sleep(2)

                
        # End of For Loop
        db_conn = db2utils.get_connection()
        sql = f'''SELECT ID, STATUS, TO_CHAR(FIRST_UPDATED,'YYYY-MM-DD HH.MI.SS') as FIRST_UPDATED, 
                TO_CHAR(LAST_UPDATED,'YYYY-MM-DD HH.MI.SS') as LAST_UPDATED FROM FINAL TABLE 
                (UPDATE EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS SET STATUS = 'APPLY_NLP' where ID = {submission_id})
                '''

        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_list = []
        if result:         
            result_list.append(result)

        result_dict = {}
        result_dict["result"] = result_list
        result_dict["status"] = "SUCCESS"
        
        return result_dict

    except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}
        result_dict["error"] = err
        result_dict["status"] = "FAILURE"        
        return result_dict

    return {"result": "Flow should not reach here"}

    
if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_doc_converto_txt.doc_convert_to_txt
    param = {
        'cos_everest_submission_bucket':'everest-submission-bucket',      
        'submission_id':61 ,
        'submissions_data_folder':'submission_documents_data' ,
        'mode':'RUNTIME'
    }

    # p_json = json.dumps(param)

    main(param)

