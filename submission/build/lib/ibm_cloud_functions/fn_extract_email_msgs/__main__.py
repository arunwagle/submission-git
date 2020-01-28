import logging
import os
from os import walk
import shutil
import glob
import importlib
import zipfile
import json
# useful tool for extracting information from XML
import re
# to pretty print our xml:
import xml.dom.minidom
import uuid
import extract_msg

import ibm_db
import ibm_db_dbi

from submission.utils import cosutils, db2utils
from submission.utils.attachment import EmailAttachmentClass

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)

OBJECT_STORAGE_EMAIL_ATTACHMENTS_ROOT_FOLDER = "submission_documents_data"


def main(params):
    logging.info('Calling extract_outlook_msg.')

    try:

        cos_everest_submission_bucket = params.get(
            "cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")

        object_id = params.get("object_id", None)
        if object_id is None or "":
            raise Exception("Pass message id")

        # Create a directory on the local drive
        object_storage_key_prefix = OBJECT_STORAGE_EMAIL_ATTACHMENTS_ROOT_FOLDER + "/runtime"    
        
        # with DB2DBConnection() as db_conn:

        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        sql = f'''SELECT ID, DOCUMENT_NAME, ENCODED_ID, HEX(ENCODED_ID) as MSG_DOCUMENT_ID FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS where ID={object_id}'''
        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_both(stmt)
        msg_object_storage_key = None
        msg_document_id = None
        msg_id = None
        if result:
            msg_id = result["ID"]
            msg_object_storage_key = result["DOCUMENT_NAME"]
            msg_encoded_id = result["ENCODED_ID"]
            msg_document_id = result["MSG_DOCUMENT_ID"]

        else:
            raise Exception("No email message document found")

        email_message_bytes = cosutils.get_item(
            cos_everest_submission_bucket, msg_object_storage_key)

        # extract attachments
        msg = extract_msg.Message(
            email_message_bytes, attachmentClass=EmailAttachmentClass)

        # save message body
        # self.__crlf = '\r\n'        
        msg_from = msg.sender 
        msg_to = msg.to
        msg_cc = msg.cc
        msg_subject = msg.subject 
        msg_date = msg.date 
        msg_body = msg.body 

        msg_file_content = """
        {msg_from}
        {msg_to}
        {msg_cc}
        {msg_subject}
        {msg_date}


        {msg_body}
        """.format(msg_from=msg_from, msg_to=msg_to, msg_cc=msg_cc, msg_subject=msg_subject, msg_date=msg_date, msg_body=msg_body)

        print (msg_file_content)
        object_storage_key = object_storage_key_prefix + "/" + str(msg_id)  + "/" + (msg_document_id + "_message.txt")
        return_val = cosutils.save_file (cos_everest_submission_bucket, object_storage_key, msg_file_content)
        if return_val is "SUCCESS":
            print("File Uploaded to object storage successfully")
        
            # create entries in DB2
            db_conn = db2utils.get_connection()
            print("db_conn: {}".format(db_conn))
            sql = f'''SELECT ID FROM FINAL TABLE (INSERT INTO EVERESTSCHEMA.EVRE_LEARNING_EMAIL_ATTACHMENTS (EVRE_EMAIL_MSG_ID, 
                        DOCUMENT_NAME, DOCUMENT_TYPE, CLASSIFICATION_TYPE, STATUS, USED_FOR) 
                        VALUES ({msg_id},                                  
                            '{object_storage_key}',
                            '.txt',
                            'N/A',
                            'CONVERT_TO_PDF',
                            'RUNTIME') 
                        )       
                        '''
            # print ("sql: {}".format(sql))

            stmt = ibm_db.exec_immediate(db_conn, sql)
            result = ibm_db.fetch_both(stmt)
            attachment_id = None
            if result:
                attachment_id = result["ID"]
            
            print(f'attachment_id: {attachment_id}')
        else:
            raise Exception("File upload to object storage failed")  

        attachments = msg.attachments
        
        count_attachments = len(attachments)
        print("count_attachments: {}", count_attachments)

        if count_attachments == 0:
            print('No Atatchments found for msg:: {}', msg_object_storage_key)
        else:
            attachment_dir = None
                        
            for i in range(count_attachments):
                attachment = attachments[i]
                
                attachment_id = attachment.save(object_storage_bucket_name=cos_everest_submission_bucket,
                                object_storage_key_prefix=object_storage_key_prefix,
                                save_to_object_storage=True,
                                msg_id=msg_id,
                                msg_encoded_id=msg_encoded_id,
                                msg_document_id=msg_document_id)


        sql = f'''SELECT ID, STATUS, TO_CHAR(FIRST_UPDATED,'YYYY-MM-DD HH.MI.SS') as FIRST_UPDATED, 
                TO_CHAR(LAST_UPDATED,'YYYY-MM-DD HH.MI.SS') as LAST_UPDATED FROM FINAL TABLE 
                (UPDATE EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS SET STATUS = 'CONVERT_TO_PDF' where ID = {msg_id})
                '''

        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_list = []
        if result:
            id = str(result["ID"])            
            result_list.append(result)

        json_result = {"result": result_list, "error": {}}
        print(f'json_result: {json_result}')
        return json_result

    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
        json_result = {"result": {}, "error": ibm_db.stmt_errormsg()}
        return json_result

    return {"result": "SUCCESS"}


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_extract_email_msgs.__main__
    param = {
        'cos_everest_submission_bucket': 'everest-submission-bucket',
        'object_id': 43
    }

    # p_json = json.dumps(param)

    main(param)
