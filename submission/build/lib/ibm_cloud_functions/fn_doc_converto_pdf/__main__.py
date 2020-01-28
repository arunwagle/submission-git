import logging
import os
from os import walk
import shutil
import glob
import json
import convertapi
import ibm_db, ibm_db_dbi
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
OBJECT_STORAGE_PUBLIC_URL="https://everest-submission-bucket.s3.us-south.cloud-object-storage.appdomain.cloud"

def main(params):
    logging.info('Calling fn_document_conversion.')

    try:

        cos_everest_submission_bucket = params.get("cos_everest_submission_bucket", None)
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

        object_storage_key = submissions_data_folder + "/" + mode + "/" + submission_id 
        
        regex = r"^" + object_storage_key + ".*$"
        
        file_keys = cosutils.get_bucket_contents(cos_everest_submission_bucket, regex)
        
        extensions = ['.docx','.doc', 'pptx']
    
        for key in file_keys:
            
            if key.endswith(tuple(extensions)) : 
                file_name = os.path.basename(key)    
                file_name_without_ext, file_extension = os.path.splitext(file_name)    
                
                url = OBJECT_STORAGE_PUBLIC_URL + "/" + object_storage_key + "/" + quote(file_name)
                PARAMS = {"apikey": convertio_api_key, "input": "url", "file": url , "outputformat": "pdf"}
                
                print (url)

                # sending get request and saving the response as response object 
                r = requests.post(url = CONVERT_IO_URL, data=json.dumps(PARAMS), stream=True) 
                
                return_val = json.loads(r.text)
                print ("1......return_val::{}", return_val)
                                
                status = return_val["status"]
                code = return_val["code"]               

                if code == 200 and status == "ok":
                    id = return_val["data"]["id"]
                    print ("converted document id::", id)
                    check_status_url = CONVERT_IO_URL + "/" + id + "/status"
                    print ("check_status_url::", check_status_url)
                    while True:                
                        r = requests.get(url = check_status_url) 
                        return_val = json.loads(r.text)
                        print ("2.......status::return_val::", return_val)
                        status = return_val["status"]
                        code = return_val["code"]
                        if code == 200 and status == "ok":
                            step = return_val["data"]["step"]
                            step_percent = return_val["data"]["step_percent"]
                            if step == "finish" and step_percent == 100:
                                id = return_val["data"]["id"]
                                print ("Get content, store in object storage and update db2 and exist")
                               
                                # get content
                                get_result_url = CONVERT_IO_URL + "/" + id + "/dl/base64"
                                print ("status::get_result_url::", get_result_url)
                                r = requests.get(url = get_result_url) 
                                return_val = json.loads(r.text)
                                
                                status = return_val["status"]
                                code = return_val["code"]
                                if code == 200 and status == "ok":
                                    content = return_val["data"]["content"]

                                    pdf_object_storage_key = object_storage_key + "/" + "final_pdf"  + "/" + file_name_without_ext + ".pdf"
                                    print("cos_everest_submission_bucket: {}: pdf_object_storage_key: {} ".format(cos_everest_submission_bucket, pdf_object_storage_key))    
                                    
                                    # Write attachments to the object storage                
                                    return_val = cosutils.save_file (cos_everest_submission_bucket, pdf_object_storage_key, base64.b64decode(content))


                                    db_conn = db2utils.get_connection()
                                    print("db_conn: {}".format(db_conn))
                                    sql = f'''SELECT ID FROM FINAL TABLE (INSERT INTO EVERESTSCHEMA.EVRE_LEARNING_EMAIL_ATTACHMENTS (EVRE_EMAIL_MSG_ID, 
                                                DOCUMENT_NAME, DOCUMENT_TYPE, CLASSIFICATION_TYPE, STATUS, USED_FOR, DESCRIPTION) 
                                                VALUES ({submission_id},                                  
                                                    '{pdf_object_storage_key}',
                                                    '.pdf',
                                                    'N/A',
                                                    'N',
                                                    'RUNTIME',
                                                    'CONVERTED_FILE') 
                                                )       
                                                '''
                                    print ("sql: {}".format(sql))

                                    stmt = ibm_db.exec_immediate(db_conn, sql)
                                    result = ibm_db.fetch_both(stmt)
                                    attachment_id = None
                                    if result:
                                        attachment_id = result["ID"]
                                                                        

                                break
                            else:
                                time.sleep(2)

                
                # extracting data in json format 


            
        # print(data)

    except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as err:
        logging.exception(err)
        json_result = json.dumps(err)    
        
    return {"result": "dd"}

    
if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_doc_converto_pdf.__main__
    param = {
        'cos_everest_submission_bucket':'everest-submission-bucket',      
        'submission_id':'43' ,
        'submissions_data_folder':'submission_documents_data' ,
        'mode':'runtime'
    }

    # p_json = json.dumps(param)

    main(param)

