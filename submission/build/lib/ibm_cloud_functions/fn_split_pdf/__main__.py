import logging
import os
from os import walk
import shutil
import glob
import json
from PyPDF2 import PdfFileReader, PdfFileWriter
import ibm_db
import ibm_db_dbi
# importing the requests library
import requests
import base64
import time
from urllib.parse import quote
from submission.utils import cosutils, db2utils
from io import BytesIO
from io import StringIO

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)

OBJECT_STORAGE_PUBLIC_URL = "https://everest-submission-bucket.s3.us-south.cloud-object-storage.appdomain.cloud"


def main(params):
    logging.info('Calling fn_split_pdf.')

    cos_everest_submission_bucket = params.get(
        "cos_everest_submission_bucket", None)
    if cos_everest_submission_bucket is None or "":
        raise Exception("Pass location of the bucket")

    final_pdf_folder = params.get("final_pdf_folder", None)
    if final_pdf_folder is None or "":
        raise Exception("Pass pdf folder to split files")

    submissions_data_folder = params.get("submissions_data_folder", None)
    if submissions_data_folder is None or "":
        raise Exception("Pass submissions_data_folder")

    submission_id = params.get("submission_id", None)
    if submission_id is None or "":
        raise Exception("Pass submission_id")

    document_id = params.get("document_id", None)
    if document_id is None or "":
        raise Exception("Pass document_id")

    mode = params.get("mode", None)
    if mode is None or "":
        raise Exception("Pass mode")

    object_storage_key = submissions_data_folder + "/" + \
        mode + "/" + submission_id + "/" + final_pdf_folder

    extensions = ['pdf']
    regex = r"^" + object_storage_key + ".*$"

    file_keys = cosutils.get_bucket_contents(
        cos_everest_submission_bucket, regex)

    for key in file_keys:

        if key.endswith(tuple(extensions)):
            file_name = os.path.basename(key)
            file_name_without_ext, file_extension = os.path.splitext(file_name)

            pdf_file_bytes = cosutils.get_item(
                cos_everest_submission_bucket, key)

            db_conn = db2utils.get_connection()
            print("db_conn: {}".format(db_conn))
            sql = f'''SELECT ID FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_ATTACHMENTS 
            where  EVRE_EMAIL_MSG_ID={submission_id} and DOCUMENT_NAME='{key}' and DOCUMENT_TYPE='.pdf' '''
            print("sql: {}".format(sql))

            stmt = ibm_db.exec_immediate(db_conn, sql)
            result = ibm_db.fetch_both(stmt)
            pdf_id = None
            if result:
                pdf_id = result["ID"]

            # read pdf
            pdf = PdfFileReader(BytesIO(pdf_file_bytes))
            num_of_pages = pdf.getNumPages()
            print("num_of_pages:: {} ", num_of_pages)

            for page in range(num_of_pages):
                pdf_writer = PdfFileWriter()
                pdf_writer.addPage(pdf.getPage(page))

                split_pdf_dir = "split_pdf_dir"
                output_filename_key = '{}/{}/{}_page_{}.pdf'.format(
                    object_storage_key, split_pdf_dir, file_name_without_ext, page+1)
                tmp = BytesIO()
                pdf_writer.write(tmp)

                tmp.seek(0)
                output_page_bytes = tmp.read()
                # print("Bytes:: {} ", output_page_bytes)

                return_val = cosutils.save_file(
                    cos_everest_submission_bucket, output_filename_key, output_page_bytes)
                if return_val is "SUCCESS":
                    print(
                        "File Uploaded to object storage successfully:: {} ", output_filename_key)
             
                db_conn = db2utils.get_connection()
                print("db_conn: {}".format(db_conn))
                sql = f'''SELECT ID FROM FINAL TABLE (INSERT INTO EVERESTSCHEMA.EVRE_LEARNING_SPLIT_CONTENT (EVRE_EMAIL_MSG_ID, EVRE_LEARNING_EMAIL_ATTACHMENTS_ID,
                            DOCUMENT_NAME, DOCUMENT_TYPE, CLASSIFICATION_TYPE, STATUS, USED_FOR, DESCRIPTION) 
                            VALUES ({submission_id}, 
                                {pdf_id},                                 
                                '{output_filename_key}',
                                '.pdf',
                                'N/A',
                                'N',
                                'RUNTIME',
                                'SPLIT_FILE') 
                            )       
                            '''
                print("sql: {}".format(sql))

                stmt = ibm_db.exec_immediate(db_conn, sql)
                result = ibm_db.fetch_both(stmt)
                attachment_id = None
                if result:
                    attachment_id = result["ID"]

    return {"result": "SUCCESS"}


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_split_pdf.__main__
    param = {
        'cos_everest_submission_bucket': 'everest-submission-bucket',
        'final_pdf_folder': 'final_pdf',
        'document_id': '43',
        'submission_id': '43',
        'submissions_data_folder': 'submission_documents_data',
        'mode': 'runtime'
    }

    # p_json = json.dumps(param)

    main(param)
