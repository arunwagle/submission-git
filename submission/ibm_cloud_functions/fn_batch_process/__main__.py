import logging
import os
from os import walk
import shutil
import glob
import importlib
import zipfile
import json
import time

import uuid 
import extract_msg

import ibm_db, ibm_db_dbi

from submission.utils import cosutils, db2utils
from submission.ibm_cloud_functions.fn_extract_email_msgs import extract_email_msgs
from submission.ibm_cloud_functions.fn_doc_converto_pdf import doc_convert_to_pdf
from submission.ibm_cloud_functions.fn_split_pdf import split_pdf
from submission.ibm_cloud_functions.fn_doc_converto_txt import doc_convert_to_txt

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)


def run_doc_convert_to_txt (params):

    try:
        
        cos_everest_submission_bucket = params.get(
            "cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")
        
        mode = params.get(
            "mode", None)
        if mode is None or "":
            raise Exception("Pass RUNTIME or TRAINING")

        status = params.get(
            "status", None)
        if status is None or "":
            raise Exception("Pass status ")   

        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        
        if status :
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                    where ID > 44 and USED_FOR = '{mode}' and status = '{status}' order by ID '''
        else : 
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                where USED_FOR = '{mode}'  order by ID ''' 

        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_dict = {}
        while result:
            id = str(result["ID"])            
            mode = result["USED_FOR"]
            

            param = {
                'cos_everest_submission_bucket':'everest-submission-bucket',      
                'submission_id':id ,
                'submissions_data_folder':'submission_documents_data' ,
                'mode': mode
            }

            doc_convert_to_txt.main(param)
            # time.sleep(2)
            print(f'doc_convert_to_txt for : {id, param}')
            
            result = ibm_db.fetch_assoc(stmt)
            
               
                    
        result_dict = {}        
        result_dict["status"] = "SUCCESS"
    except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}        
        result_dict["status"] = "FAILURE"

    return {"result": "This flow should get executed"}

def run_split_pdf (params):

    try:
        
        cos_everest_submission_bucket = params.get(
            "cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")

        mode = params.get(
            "mode", None)
        if mode is None or "":
            raise Exception("Pass RUNTIME or TRAINING")

        status = params.get(
            "status", None)
        if status is None or "":
            raise Exception("Pass status ")   

        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        
        if status :
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                    where USED_FOR = '{mode}' and status = '{status}' order by ID '''
        else : 
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                where USED_FOR = '{mode}'  order by ID ''' 

        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_dict = {}
        while result:
            id = str(result["ID"])            
            mode = result["USED_FOR"]
            
            param = {
                'cos_everest_submission_bucket': cos_everest_submission_bucket,
                'final_pdf_folder': 'final_pdf',
                'submission_id': id,
                'submissions_data_folder': 'submission_documents_data',
                'mode': mode
            }
            split_pdf.main(param)
            # time.sleep(2)
            print(f'Split PDF for : {id, param}')
            
            result = ibm_db.fetch_assoc(stmt)
            
               
                    
        result_dict = {}        
        result_dict["status"] = "SUCCESS"
    except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}        
        result_dict["status"] = "FAILURE"

    return {"result": "This flow should get executed"}

def run_convert_to_pdf (params):

    try:
        
        cos_everest_submission_bucket = params.get(
            "cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")

        mode = params.get(
            "mode", None)
        if mode is None or "":
            raise Exception("Pass RUNTIME or TRAINING")

        status = params.get(
            "status", None)
        if status is None or "":
            raise Exception("Pass status ")   

        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        
        if status :
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                    where USED_FOR = '{mode}' and status = '{status}' order by ID '''
        else : 
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                where USED_FOR = '{mode}'  order by ID ''' 
        
        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_dict = {}
        while result:
            id = str(result["ID"])            
            mode = result["USED_FOR"]
            param = {
                'cos_everest_submission_bucket': cos_everest_submission_bucket,
                'submission_id': id,
                'submissions_data_folder':'submission_documents_data' ,
                'mode': mode
            }
            doc_convert_to_pdf.main(param)
            # time.sleep(2)
            print(f'Converting to PDF for : {id, param}')
            
            result = ibm_db.fetch_assoc(stmt)
            
               
                    
        result_dict = {}        
        result_dict["status"] = "SUCCESS"
    except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}        
        result_dict["status"] = "FAILURE"

    return {"result": "This flow should get executed"}

def run_extract_email_msg (params):

    try:
        
        cos_everest_submission_bucket = params.get(
            "cos_everest_submission_bucket", None)
        if cos_everest_submission_bucket is None or "":
            raise Exception("Pass location of the bucket")

        mode = params.get(
            "mode", None)
        if mode is None or "":
            raise Exception("Pass RUNTIME or TRAINING")

        limit = params.get(
            "limit", None)        

        db_conn = db2utils.get_connection()
        print("db_conn: {}".format(db_conn))

        if limit :
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                    where USED_FOR = '{mode}' order by ID LIMIT {limit}'''
        else : 
            sql = f'''SELECT ID, USED_FOR FROM EVERESTSCHEMA.EVRE_LEARNING_EMAIL_MSGS 
                    where USED_FOR = '{mode}' order by ID '''                  

        print("sql: {}".format(sql))

        stmt = ibm_db.exec_immediate(db_conn, sql)
        result = ibm_db.fetch_assoc(stmt)

        result_dict = {}
        while result:
            id = str(result["ID"])            
            mode = result["USED_FOR"]
            param = {
                'cos_everest_submission_bucket': cos_everest_submission_bucket,
                'submission_id': id,
                'mode': mode
            }

            print(f'Extracting Email message for : {id, param}')
            extract_email_msgs.main(param)
            result = ibm_db.fetch_assoc(stmt)
               
                    
        result_dict = {}        
        result_dict["status"] = "SUCCESS"
    except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as err:
        logging.exception(err)
        result_dict = {}        
        result_dict["status"] = "FAILURE"

    return {"result": "This flow should get executed"}


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_batch_process.__main__
    # params = {
    #     'cos_everest_submission_bucket':'everest-submission-bucket'   ,
    #     'mode': 'RUNTIME',
    #     'limit': 21
    # }
    # run_extract_email_msg(params)

    # params = {
    #     'cos_everest_submission_bucket':'everest-submission-bucket'   ,
    #     'mode': 'RUNTIME',
    #     'status': 'CONVERT_TO_PDF'
    # }
    # run_convert_to_pdf(params)

    # params = {
    #     'cos_everest_submission_bucket':'everest-submission-bucket'   ,
    #     'mode': 'RUNTIME',
    #     'status': 'SPLIT_PDF'
    # }
    # run_split_pdf(params)

    params = {
        'cos_everest_submission_bucket':'everest-submission-bucket'   ,
        'mode': 'RUNTIME',
        'status': 'STANDARDIZE_TO_TXT'
    }
    run_doc_convert_to_txt(params)
    
    

