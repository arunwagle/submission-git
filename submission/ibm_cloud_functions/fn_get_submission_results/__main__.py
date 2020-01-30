import logging
import os
from os import walk
import shutil
import glob
import json
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

        cos_everest_submission_bucket = params.get("cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")  

        
        submission_id = params.get("submission_id", None)
        if submission_id is None or "":
            raise Exception("Pass submission_id")

        submissions_data_folder = params.get("submissions_data_folder", None)
        if submissions_data_folder is None or "":
            raise Exception("Pass submissions_data_folder")

        standardized_txt_dir = params.get("standardized_txt_dir", None)
        if standardized_txt_dir is None or "":
            raise Exception("Pass standardized_txt_dir")

        mode = params.get("mode", None)
        if mode is None or "":
            raise Exception("Pass mode")

        model_id = params.get("model_id", None)
        if model_id is None or "":
            raise Exception("Pass model_id")


        object_storage_key = submissions_data_folder + "/" + \
            mode + "/" + str(submission_id) + "/" + standardized_txt_dir

        extensions = ['txt']
        regex = r"^" + object_storage_key + ".*$"


        file_keys = cosutils.get_bucket_contents(
            cos_everest_submission_bucket, regex)

        
        nlu_service = watson_nlu_utils.inst()
        results_dict = {}
        nlu_results_list = []
        for key in file_keys:
            print("Processing file:: {}",  file_keys)

            txt_file_bytes = cosutils.get_item(
                    cos_everest_submission_bucket, key)

            text = txt_file_bytes.decode("utf-8")
            # print("text:: {}",  text)

            if text is Not None:
                nlu_results = watson_nlu_utils.get_result(nlu_service, model_id, text)
            nlu_results_list.append(nlu_results)


        # db_conn = db2utils.get_connection()
        # print("db_conn: {}".format(db_conn))

        # sql = f'''SELECT ID, DOCUMENT_NAME, STATUS, TO_CHAR(FIRST_UPDATED,'YYYY-MM-DD HH.MI.SS') as FIRST_UPDATED, 
        #     TO_CHAR(LAST_UPDATED,'YYYY-MM-DD HH.MI.SS') as LAST_UPDATED FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
        #         where USED_FOR = 'RUNTIME' order by ID '''

        # print("sql: {}".format(sql))

        # stmt = ibm_db.exec_immediate(db_conn, sql)
        # result = ibm_db.fetch_assoc(stmt)

        # result_list = []
        # while result:
        #     id = str(result["ID"])            
            
        #     result = ibm_db.fetch_assoc(stmt)
        #     result_list.append(result)
        
        result_dict = {}
        result_dict["result"] = nlu_results_list
        result_dict["status"] = "SUCCESS"

        print (result_dict)
        return result_dict

    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}
        result_dict["error"] = err
        result_dict["status"] = "FAILURE"        
        return result_dict

    return {"result": "Flow should not reach here"}


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_get_submission_results.__main__
    param = {
        'cos_everest_submission_bucket': 'everest-submission-bucket',
        'standardized_txt_dir': 'standardized_txt_dir',
        'submission_id': 46,
        'submissions_data_folder': 'submission_documents_data',
        'mode': 'runtime',
        'model_id': '0e2be798-0ef3-426d-a01e-c5110f0ecd5e'
    }

    # p_json = json.dumps(param)

    main(param)
