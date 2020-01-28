import logging
import ibm_db, ibm_db_dbi
from threading import local
from os import environ
import json

t_local = local()

class DB2DBConnection:
    """
    `DB2DBConnection` makes the connection to the DB,
    and provides it within a context. Once the control flow
    exits the context, the connection handles the
    transaction level operations like commit, rollback, and
    close. It also handles nested DB connections by using
    the same connection throughout the control and transaction
    operations are handled by the boundary connection.

    Always surround the context with a try-except block to
    handle errors in case the connection itself fails due to
    any unknown/unhandled reason

    Usage:

        try:
            with DB2DBConnection() as db_conn:
                with db_conn.cursor() as cursor:
                    cursor.execute('''select *
                                      from rrf_request
                                      order by entity_request_id desc
                                      limit 1''')
                    result = cursor.fetchall()
                    print(result)
                # cursor is automatically closed here releasing all its resources
                # db_conn is still open here so other cursors maybe used
            # db_conn is closed here
        except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as db_error:
            logging.exception(db_error)

    """
    
# conn_str='database=BLUDB;hostname=db2w-tiggaci.us-east.db2w.cloud.ibm.com;port=50001;protocol=tcpip;uid=bluadmin;pwd=H1_8dZY@YOuHF9BHmT7ZWhdBdQX@k'
# db2cli writecfg add -dsn alias1 -database BLUDB -host db2w-tiggaci.us-east.db2w.cloud.ibm.com -port 50001 SecurityTransportMode=SSL
# db2cli registerdsn -add -dsn alias1
# db2cli validate -dsn name1 -connect -user bluadmin -passwd H1_8dZY@YOuHF9BHmT7ZWhdBdQX@k

    def __init__(self):
        self.database = environ.get('DB2_DATABASE', 'BLUDB')
        self.host = environ.get('DB2_HOSTNAME', 'db2w-tiggaci.us-east.db2w.cloud.ibm.com')
        self.port = environ.get('DB2_PORT', 50001)
        self.protocol = environ.get('DB2_PROTOCOL', 'TCPIP')
        self.user = environ.get('DB2_UID', 'bluadmin')
        self.password = environ.get('DB2_PASSWORD', 'H1_8dZY@YOuHF9BHmT7ZWhdBdQX@k')
        # self.ssl = environ.get('DB2_PASSWORD', 'SSL')

        self.config_string = "DATABASE=%s;HOSTNAME=%s;PORT=%d;PROTOCOL=%s;UID=%s;PWD=%s;" \
                             % (self.database, self.host, self.port, self.protocol, self.user, self.password)

        self.SSL_DSN = "database=BLUDB;hostname=db2w-tiggaci.us-east.db2w.cloud.ibm.com;port=50001;protocol=tcpip;uid=bluadmin;pwd=H1_8dZY@YOuHF9BHmT7ZWhdBdQX@k"
        self.db_connection = None    

    def __enter__(self):

        try:
            self.boundary = False
            self.db_connection = getattr(t_local, '_conn', None)
            if self.db_connection is None:
                self.boundary = True
                print("self.config_string::" + self.config_string)
                self.db_connection = ibm_db.connect(self.SSL_DSN, '', '')
                print("self.db_connection::" + str(self.db_connection))
                setattr(t_local, '_conn', str(self.db_connection))
        except (ibm_db.conn_error, ibm_db.conn_errormsg, Exception) as db_error:
            print("db_error::" + str(db_error))            
            # raise db_error
        return self.db_connection


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.boundary:
            if exc_type is not None:
                ibm_db.rollback(self.db_connection)
                logging.error(f'{exc_type.__name__}: {exc_val}')
            else:
                ibm_db.commit(self.db_connection)
                print("commit transaction")
            ibm_db.close(self.db_connection)
            delattr(t_local, '_conn')
        elif exc_type is not None:
            raise exc_type(exc_val)



if __name__ == '__main__':

    """For usage reference"""

    # conn = DB2DBConnection().call ()
    # sql = "Select * from GOSALES.BRANCH"
    # stmt = ibm_db.exec_immediate(conn, sql)
    # data = ibm_db.fetch_both(stmt)

    try:
        with DB2DBConnection() as db_conn:
            # sql = f'''SELECT encoded_id FROM FINAL TABLE (INSERT INTO EVERESTSCHEMA.evre_learning_email_msgs (encoded_id, 
            #                 business_segment_id, status, document_name) 
            #                 VALUES (GENERATE_UNIQUE(), 
            #                     1,
            #                     'N',
            #                     'testkey') 
            #                 )       
            #                 '''
            sql = f'''SELECT ID, HEX(encoded_id) as encoded_id FROM EVERESTSCHEMA.evre_learning_email_msgs'''
                
            stmt = ibm_db.exec_immediate(db_conn, sql)
            result = ibm_db.fetch_both(stmt)
            msg_document_id = None
            if result:
                msg_document_id = result["ENCODED_ID"]
                
            print(f'encode_id: {msg_document_id}')
    except (ibm_db.conn_error, ibm_db. conn_errormsg, Exception) as err:
        logging.exception(err)
