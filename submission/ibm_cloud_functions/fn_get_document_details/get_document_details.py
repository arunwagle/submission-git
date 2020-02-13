import logging
import os
from os import walk
import shutil
import glob
import json
from collections import defaultdict
from itertools import chain
import ibm_db
import ibm_db_dbi
from submission.utils import watson_nlu_utils, cosutils, db2utils


logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)

OBJECT_STORAGE_PUBLIC_URL = "https://everest-submission-bucket.s3.us-south.cloud-object-storage.appdomain.cloud"


def main(params):
    logging.info('Calling fn_get_submission_results')

    try:
        
        submission_id = params.get("submission_id", None)
        if submission_id is None or "":
            raise Exception("Pass submission_id")

        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        sql = f'''SELECT DOCUMENT_NAME, CLASSIFICATION_TYPE FROM EVERESTSCHEMA.evre_learning_email_attachments 
                where EVRE_EMAIL_MSG_ID = {submission_id}  '''

        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_list = []
        while result:             
            result_list.append(result)
            result = ibm_db.fetch_assoc(stmt)
            

        json_result = {"result": result_list, "error": {}}
        print(f'json_result: {json_result}')
        result_dict = {}
        result_dict["result"] = result_list
        result_dict["status"] = "SUCCESS"
        return result_dict

        return nlu_results_dict

    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}
        result_dict["error"] = err
        result_dict["status"] = "FAILURE"
        return result_dict

    return {"result": "Flow should not reach here"}



if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_get_document_details.get_document_details
    param = {
        'submission_id': 54        
    }

    # p_json = json.dumps(param)

    main(param)
