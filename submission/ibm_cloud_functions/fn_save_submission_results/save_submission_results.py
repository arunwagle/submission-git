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
            mode + "/" + str(submission_id)

        output_object_storage_key = submissions_data_folder + "/" + \
            mode + "/" + str(submission_id) + "/" + \
            "nlu_results" + "/" + "output.json"

        # + "/" + standardized_txt_dir

        extensions = ['txt']
        regex = r"^" + object_storage_key + ".*txt$"

        file_keys = cosutils.get_bucket_contents(
            cos_everest_submission_bucket, regex)

        nlu_service = watson_nlu_utils.inst()
        results_dict = {}
        nlu_results_list = []
        for key in file_keys:
            print("Processing file:: {}",  file_keys)
            if key.endswith(tuple(extensions)):
                txt_file_bytes = cosutils.get_item(
                    cos_everest_submission_bucket, key)

                text = txt_file_bytes.decode("utf-8")
                print("text:: ",  len(text.strip()))

                nlu_results = None
                if text is not None and len(text.strip()) != 0:
                    nlu_results = watson_nlu_utils.get_result(
                        nlu_service, model_id, text)

                nlu_results_list.append(nlu_results)

        # get Final cleaned results
        nlu_results_dict = {}
        nlu_response = get_clean_results(nlu_results_list)
        nlu_results_dict["result"] = nlu_response
        
        res_bytes = str(nlu_results_dict).encode('utf-8')
        print("res_bytes::", res_bytes)
        

        #  store in object storage
        return_val = cosutils.save_file(
            cos_everest_submission_bucket, output_object_storage_key, res_bytes)
        if return_val is "SUCCESS":
            print(
                "File Uploaded to object storage successfully:: {} ", output_object_storage_key

            )

        validation_status = get_validation_status(nlu_response)

        print("validation_status", validation_status["status"])

        db_conn = db2utils.get_connection()
        sql = f'''SELECT ID, STATUS, TO_CHAR(FIRST_UPDATED,'YYYY-MM-DD HH.MI.SS') as FIRST_UPDATED,
                TO_CHAR(LAST_UPDATED,'YYYY-MM-DD HH.MI.SS') as LAST_UPDATED FROM FINAL TABLE
                (UPDATE EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS SET STATUS = '{validation_status["status"]}' where ID = {submission_id})
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

        print(result_dict)
        return result_dict

    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}
        result_dict["error"] = err
        result_dict["status"] = "FAILURE"
        return result_dict

    return {"result": "Flow should not reach here"}


def merge_list_of_dicts_by_key(list_of_dicts, key):
    merged = defaultdict(dict)

    for dictionary in list_of_dicts:
        merged[dictionary[key]].update(dictionary)

    return merged.values()


def get_validation_status(nlu_response):
    validation_results = {}

    validation_results["status"] = "COMPLETED"
    validation_results["message"] = "SUCCESS"

    if nlu_response is None:
        validation_results["status"] = "VALIDATION_ERROR"
        validation_results["message"] = "No Data Found"
    else:

        for key, value_list in nlu_response.items():

            if key not in ("FN_INSURED_VALUE", "POLICY_EFF_DT_VALUE", "POLICY_EXP_DT_VALUE", "TOTAL_TIV_VALUE"):
                validation_results["status"] = "VALIDATION_ERROR"
                validation_results["message"] = "Required fields missing: FN_INSURED_VALUE, POLICY_EFF_DT_VALUE, POLICY_EXP_DT_VALUE, TOTAL_TIV_VALUE "
                break
                
                
    return validation_results


def get_clean_results(nlu_results_list):
    print("nlu_results_list::", nlu_results_list)

    merged_dict = defaultdict(list)
    for nlu_result_dict in nlu_results_list:
        if nlu_result_dict is None:
            continue
        
        for key, value in nlu_result_dict.items():
            # if value not in merged_dict.values():
            merged_dict[key].append(value)

    result = {}
    for key, value_list in merged_dict.items():
        # print ("key::", key)
        new_value = value_list
        if key in ("FN_INSURED_ADDR_VALUE", "POLICY_EFF_DT_VALUE", "POLICY_EXP_DT_VALUE", "TOTAL_TIV_VALUE", "FN_INSURED_ADDR_VALUE", "POLICY_LIMIT_VALUE"):
            new_value = list(dict.fromkeys(value_list))
        else:
            flat_list = [y for x in value_list for y in x]
            if key not in "AGENT_LIST":
                new_value = list(dict.fromkeys(flat_list))
            else:
                new_value = merge_list_of_dicts_by_key(
                    chain(flat_list), "AGENT_NAME_VALUE")

        result[key] = new_value

    return dict(result)


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_save_submission_results.save_submission_results
    param = {
        'cos_everest_submission_bucket': 'everest-submission-bucket',
        'standardized_txt_dir': 'standardized_txt_dir',
        'submission_id': 46,
        'submissions_data_folder': 'submission_documents_data',
        'mode': 'RUNTIME',
        'model_id': 'c85996b7-d62e-4158-a80d-47089cf0fd4e'
    }

    # p_json = json.dumps(param)

    main(param)
