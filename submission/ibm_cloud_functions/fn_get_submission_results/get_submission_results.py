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

        nlp_results_dir = params.get("nlp_results_dir", None)
        if nlp_results_dir is None or "":
            raise Exception("Pass nlp_results_dir")

        mode = params.get("mode", None)
        if mode is None or "":
            raise Exception("Pass mode")     

        object_storage_key = submissions_data_folder + "/" + \
            mode + "/" + str(submission_id) + "/" + \
            "nlu_results" + "/" + "output.json"

       txt_file_bytes = cosutils.get_item(
                    cos_everest_submission_bucket, object_storage_key)

        text = txt_file_bytes.decode("utf-8")

        nlu_results_dict = json.loads(text) 
        print("nlu_results_dict::", nlu_results_dict)        
        nlu_results_dict["status"] = "SUCCESS"
        
        return nlu_results_dict

    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}
        result_dict["error"] = err
        result_dict["status"] = "FAILURE"
        return result_dict

    return {"result": "Flow should not reach here"}



if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_get_submission_results.get_submission_results
    param = {
        'cos_everest_submission_bucket': 'everest-submission-bucket',
        'nlp_results_dir': 'nlp_results',
        'submission_id': 46,
        'submissions_data_folder': 'submission_documents_data',
        'mode': 'RUNTIME',
        
    }

    # p_json = json.dumps(param)

    main(param)
