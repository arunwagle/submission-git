import json
import ibm_db

SSL_DSN = "DATABASE=BLUDB;HOSTNAME=db2w-tiggaci.us-east.db2w.cloud.ibm.com;PORT=50001;PROTOCOL=TCPIP;UID=bluadmin;PWD=H1_8dZY@YOuHF9BHmT7ZWhdBdQX@k;Security=SSL;"

def get_connection():
    conn = ibm_db.connect(SSL_DSN, "", "")

    return conn

def execute_query(sql):
    conn = ibm_db.connect(SSL_DSN, "", "")

    stmt = ibm_db.exec_immediate(conn, sql)
    data = ibm_db.fetch_assoc(stmt)

    dict_list = []

    # if data:
    #     print(data['BRANCH_CODE'])
    #     # dict_list.append(data)
    #     data = ibm_db.fetch_both(stmt)

    while data:
        dict_list.append(data)
        data = ibm_db.fetch_assoc(stmt)


    json_data = json.dumps(dict_list)
    print(json_data)

    return json_data

def execute(sql):

    try:
        conn = ibm_db.connect(SSL_DSN, "", "")
        stmt = ibm_db.exec_immediate(conn, sql)
        # ibm_db.bind_param(stmt, 1, animal)
    except:
        print
        "Transaction couldn't be completed:", ibm_db.stmt_errormsg()
    else:
        print
        "Transaction complete."

    return "SUCCESS"


if __name__ == "__main__":
    execute_query("SELECT ID, HEX(encoded_id) as encoded_id FROM EVERESTSCHEMA.evre_learning_email_msgs")
    # SQL = "INSERT INTO REQUEST (encoded_id, submission_id, entity_name, country_code, status) VALUES ('XXXX', 1, 'Test', 'US', 'ACTIVE')"
    # execute(SQL)


