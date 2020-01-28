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

import asyncio

import ibm_db
import ibm_db_dbi
from submission.framework.db2_settings import DB2DBConnection
from submission.utils import cosutils, db2utils, watsondiscoveryutils
from submission.ibm_cloud_functions.fn_extract_email_msgs.attachment import EmailAttachmentClass

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)


SUBMISSION_BUCKET = "everest-submission-bucket"

SUBMISSION_DATA_FOLDER = "submission_documents_data/training"

DOC_TYPE_TO_PROCESS = [".DOCX", ".DOC", ".docx", ".doc", ".PDF", ".pdf"]

WDS_ENV_ID = "b3e4ff43-07a6-46b8-b886-23108cff6904"

# For pdf, doc
WDS_SUBMISSION_GROUP1_COL_ID = "d16a19ec-46b5-42ed-a21b-d7e6a60f0f81"

# for pptx
WDS_SUBMISSION_GROUP2_COL_ID = "e1e69c19-6912-4761-adc6-c9df96a5850e"

# for excel
WDS_SUBMISSION_GROUP3_COL_ID = "e1e69c19-6912-4761-adc6-c9df96a5850e"


WDS_METADATA = {"Creator": "EverestRe System"}


def wds_upload_task(wds, cos_everest_submission_bucket, obj_storage_doc_path, file_content_type):
    print("Calling wds_upload_task")
    doc_bytes = cosutils.get_item(
        cos_everest_submission_bucket, obj_storage_doc_path)

    if doc_bytes is not None:
        last_index_of_slash = obj_storage_doc_path.rfind("/")
        folder_path = obj_storage_doc_path[0:last_index_of_slash]
        file_name = obj_storage_doc_path[last_index_of_slash + 1:]
        print("file_name::{}", file_name)
        print("folder_path::{}", folder_path)

        WDS_METADATA["folder_path"] = folder_path
        watsondiscoveryutils.upload_document(wds, environment_id=WDS_ENV_ID, collection_id=WDS_SUBMISSION_GROUP1_COL_ID,
                                            file_content=doc_bytes, filename=file_name, 
                                            file_content_type=file_content_type, metadata=json.dumps(WDS_METADATA))

    else:
        print("Key Not found in object storage: {}", obj_storage_doc_path)

def main(params):
    logging.info('Calling fn_wds_operations.')

    try:

        cos_everest_submission_bucket = params.get(
            "cos_everest_submission_bucket", SUBMISSION_BUCKET)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")

        cos_everest_submission_data_folder = params.get(
            "cos_everest_submission_data_folder", SUBMISSION_DATA_FOLDER)
        if cos_everest_submission_data_folder is None or "":
            raise Exception("Pass cos_everest_submission_data_folder")

        doc_type_to_process = params.get(
            "doc_type_to_process", DOC_TYPE_TO_PROCESS)
        if doc_type_to_process is None or "":
            raise Exception("Pass doc_type_to_process")

        # initialize watson discovery utils
        wds = watsondiscoveryutils.inst()

        # with DB2DBConnection() as db_conn:
        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        sql = f'''SELECT ID, DOCUMENT_TYPE, DOCUMENT_NAME
                FROM EVERESTSCHEMA.evre_learning_email_attachments where used_for='TRAINING' and DOCUMENT_TYPE IN {tuple(doc_type_to_process)} order by ID'''
        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_both(stmt)
        msg_id = None
        msg_encoded_id = None
        msg_document_id = None        
        while result:
            print("result::{}".format(result))
            msg_id = result["ID"]
            doc_type = result["DOCUMENT_TYPE"]
            obj_storage_doc_path = result["DOCUMENT_NAME"]
            print(f'obj_storage_doc_path: {obj_storage_doc_path}')

            # https://blogs.msdn.microsoft.com/vsofficedeveloper/2008/05/08/office-2007-file-format-mime-types-for-http-content-streaming-2/
            if doc_type.lower() == ".PDF".lower():
                file_content_type = "application/pdf"
            elif doc_type.lower() == ".DOCX".lower():
                file_content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif doc_type.lower() == ".DOC".lower():
                file_content_type = "application/msword"
            elif doc_type.lower() == ".XLSX".lower():
                file_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif doc_type.lower() == ".XLS".lower() or doc_type.lower() == ".XL".lower():
                file_content_type = "application/vnd.ms-excel"
            elif doc_type.lower() == ".XLSM".lower():
                file_content_type = "application/vnd.ms-excel.sheet.macroEnabled.12"
            elif doc_type.lower() == ".XLTM".lower():
                file_content_type = "application/vnd.ms-excel.template.macroEnabled.12"
            elif doc_type.lower() == ".XLTX".lower():
                file_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.template"
            elif doc_type.lower() == ".XLSB".lower():
                file_content_type = "application/vnd.ms-excel.sheet.binary.macroEnabled.12"
            elif doc_type.lower() == ".PPTX".lower():
                file_content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            elif doc_type.lower() == ".HTML".lower():
                file_content_type = "application/xhtml+xml"

            # task = asyncio.create_task(wds_upload_task(wds, cos_everest_submission_bucket, obj_storage_doc_path, doc_bytes, doc_type))

            # await task
            wds_upload_task(wds, cos_everest_submission_bucket,
                            obj_storage_doc_path, file_content_type)

            # iterate thru the resultset                            
            result = ibm_db.fetch_both(stmt)

    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
        json_result = json.dumps(err)

    return {"result": "Success"}


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_wds_operations.__main__
    param = {
        'cos_everest_submission_bucket': 'everest-submission-bucket'
    }

    # p_json = json.dumps(param)
    # asyncio.run(main(param))
    main(param)
