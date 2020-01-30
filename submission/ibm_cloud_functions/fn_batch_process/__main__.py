import logging
import os
from os import walk
import shutil
import glob
import importlib
import zipfile
import json
#useful tool for extracting information from XML
import re
#to pretty print our xml:
import xml.dom.minidom
import uuid 
import extract_msg

import ibm_db, ibm_db_dbi
from submission.framework.db2_settings import DB2DBConnection
from submission.utils import cosutils, db2utils
from submission.ibm_cloud_functions.fn_extract_email_msgs.attachment import EmailAttachmentClass

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)



ATTACHMENT_DIR_PREFIX = "email_attachments"
EMAIL_MESSAGE_FOLDER = "email_message_data"
SUBMISSION_DATA_FOLDER = "submission_documents_data"


def main(params):
    logging.info('Calling extract_outlook_msg.')

    try:

        cos_everest_submission_bucket = params.get("cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")    

        save_to_object_storage = params.get("save_to_object_storage", None)
        if save_to_object_storage is None or "":
            save_to_object_storage = True   

        
        # email_messages_key_list = cosutils.get_bucket_contents(cos_everest_submission_bucket, r"^email_message_data.*msg$")
        email_message_data_folder_pattern = r"^" + EMAIL_MESSAGE_FOLDER + ".*msg$"        
        email_messages_key_list = cosutils.get_bucket_contents(cos_everest_submission_bucket, email_message_data_folder_pattern)
        print("email_messages::{}".format(email_messages_key_list))

        # with DB2DBConnection() as db_conn:
      
        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        total_msgs = len(email_messages_key_list)
        msg_count = 0
        for msg_object_storage_key in email_messages_key_list:
                msg_count += 1
                print ("msg_object_storage_key: {}".format(msg_object_storage_key))
                result_dict = dict()
            
                sql = f'''SELECT ID, encoded_id, HEX(encoded_id) as msg_document_id FROM FINAL TABLE (INSERT INTO EVERESTSCHEMA.evre_learning_email_msgs (encoded_id, 
                            business_segment_id, status, document_name) 
                            VALUES (GENERATE_UNIQUE(), 
                                1,
                                'N',
                                '{msg_object_storage_key}') 
                            )       
                            '''
                # print ("sql: {}".format(sql))

                stmt = ibm_db.exec_immediate(db_conn, sql)
                result = ibm_db.fetch_both(stmt)
                msg_id = None
                msg_encoded_id= None
                msg_document_id= None
                if result:
                    msg_id = result["ID"]
                    msg_encoded_id = result["ENCODED_ID"]
                    msg_document_id = result["MSG_DOCUMENT_ID"]
                
                print(f'encode_id: {msg_encoded_id}')
                # get data in bytes from object storage
                email_message_bytes = cosutils.get_item(cos_everest_submission_bucket, msg_object_storage_key)
               
                # extract attachments
                msg = extract_msg.Message(email_message_bytes, attachmentClass = EmailAttachmentClass)                            
                attachments = msg.attachments
                count_attachments = len(attachments)
                print ("count_attachments: {}", count_attachments)
                
                if count_attachments == 0:
                    print('No Atatchments found for msg:: {}', msg_object_storage_key)
                else:
                    attachment_dir = None
                    # Create a directory on the local drive
                    if not save_to_object_storage:
                        attachment_dir = ATTACHMENT_DIR_PREFIX + "/" + msg_encoded_id
                        os.makedirs(attachment_dir, exist_ok=True)

                    object_storage_key_prefix = SUBMISSION_DATA_FOLDER
                    if(msg_count <= total_msgs/2 + 1):
                        object_storage_key_prefix += "/training"
                    else:
                        object_storage_key_prefix += "/test" 


                    id = uuid.uuid4() 
                    for i in range(count_attachments):
                        attachment = attachments[i]   
                        # root_folder = msg_object_storage_key[0:msg_object_storage_key.rfind("/")]  
                        
                        attachment.save(customPath=attachment_dir, 
                            object_storage_bucket_name=cos_everest_submission_bucket,
                            object_storage_key_prefix=object_storage_key_prefix, 
                            save_to_object_storage=save_to_object_storage,
                            msg_id=msg_id,
                            msg_encoded_id=msg_encoded_id,
                            msg_document_id=msg_document_id)
                        

    except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as err:
        logging.exception(err)
        json_result = json.dumps(err)
    
    



    return {"result": "dd"}

    
if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_extract_email_msgs.__main__
    param = {
        'cos_everest_submission_bucket':'everest-submission-bucket'      
    }

    # p_json = json.dumps(param)

    main(param)

