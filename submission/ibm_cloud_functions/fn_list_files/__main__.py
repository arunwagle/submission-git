import logging
import os
from os import walk
import shutil
import glob
import json
import ibm_db
import ibm_db_dbi
from submission.utils import cosutils, db2utils


logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)

OBJECT_STORAGE_PUBLIC_URL = "https://everest-submission-bucket.s3.us-south.cloud-object-storage.appdomain.cloud"


def main(params):
    logging.info('Calling fn_split_pdf.')

    try:

        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        sql = f'''SELECT ID, DOCUMENT_NAME, STATUS, TO_CHAR(FIRST_UPDATED,'YYYY-MM-DD HH.MI.SS') as FIRST_UPDATED, 
            TO_CHAR(LAST_UPDATED,'YYYY-MM-DD HH.MI.SS') as LAST_UPDATED FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                where USED_FOR = 'RUNTIME' order by ID '''

        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_list = []
        while result:
            id = str(result["ID"])            
            
            result = ibm_db.fetch_assoc(stmt)
            result_list.append(result)

        json_result = {"result": result_list, "error": {}}
        print(f'json_result: {json_result}')
        result_dict = {}
        result_dict["result"] = result_list
        result_dict["status"] = "SUCCESS"
        return result_dict

    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}
        result_dict["error"] = err
        result_dict["status"] = "FAILURE"        
        return result_dict

    return {"result": "Flow should not reach here"}


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_list_files.__main__
    param = {
    }

    # p_json = json.dumps(param)

    main(param)
