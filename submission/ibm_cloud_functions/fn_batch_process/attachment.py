import os
import logging
import random
import string

import ibm_db, ibm_db_dbi

from extract_msg import constants
from extract_msg.properties import Properties
from extract_msg.utils import properHex

from submission.utils import cosutils, db2utils


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# STORAGE_ACCOUNT_NAME = "everestsubmissiondata"
# STORAGE_ACCOUNT_KEY = "ETzyMX/4r4PoYRg/3M+n3ZlDC01S80Fi9xBz9vQDX+rH7pJiI67c3pp0+DOGsCTR8LgZrN+p/syrL97AhUeNlg=="


class EmailAttachmentClass(object):


    """
    Stores the attachment data of a Message instance.
    Should the attachment be an embeded message, the
    class used to create it will be the same as the
    Message class used to create the attachment.
    """

    def __init__(self, msg, dir_):
        """
        :param msg: the Message instance that the attachment belongs to.
        :param dir_: the directory inside the msg file where the attachment is located.
        """
        object.__init__(self)
        self.__msg = msg
        self.__dir = dir_
        self.__props = Properties(self._getStream('__properties_version1.0'),
            constants.TYPE_ATTACHMENT)
        # Get long filename
        self.__longFilename = self._getStringStream('__substg1.0_3707')

        # Get short filename
        self.__shortFilename = self._getStringStream('__substg1.0_3704')

        # Get Content-ID
        self.__cid = self._getStringStream('__substg1.0_3712')

        # Get attachment data
        if self.Exists('__substg1.0_37010102'):
            self.__type = 'data'
            self.__data = self._getStream('__substg1.0_37010102')
        elif self.Exists('__substg1.0_3701000D'):
            if (self.__props['37050003'].value & 0x7) != 0x5:
                raise NotImplementedError(
                    'Current version of extract_msg does not support extraction of containers that are not embedded msg files.')
                # TODO add implementation
            else:
                self.__prefix = msg.prefixList + [dir_, '__substg1.0_3701000D']
                self.__type = 'msg'
                self.__data = msg.__class__(self.msg.path, self.__prefix, self.__class__)
        else:
            # TODO Handling for special attacment types (like 0x00000007)
            raise TypeError('Unknown attachment type.')

    
    def _getStream(self, filename):
        return self.__msg._getStream([self.__dir, filename])

    def _getStringStream(self, filename):
        """
        Gets a string representation of the requested filename.
        Checks for both ASCII and Unicode representations and returns
        a value if possible.  If there are both ASCII and Unicode
        versions, then :param prefer: specifies which will be
        returned.
        """
        return self.__msg._getStringStream([self.__dir, filename])

    def Exists(self, filename):
        """
        Checks if stream exists inside the attachment folder.
        """
        return self.__msg.Exists([self.__dir, filename])

    def sExists(self, filename):
        """
        Checks if the string stream exists inside the attachment folder.
        """
        return self.__msg.sExists([self.__dir, filename])

    def save(self, contentId=False, json=False, useFileName=False, raw=False, customPath=None, customFilename=None, object_storage_bucket_name=None, object_storage_key_prefix = None, save_to_object_storage=None, msg_id=None, msg_encoded_id=None, msg_document_id=None):
        # Check if the user has specified a custom filename
        filename = None

        if customFilename is not None and customFilename != '':
            filename = customFilename
        else:
            # If not...
            # Check if user wants to save the file under the Content-id
            if contentId:
                filename = self.__cid
            # If filename is None at this point, use long filename as first preference
            if filename is None:
                filename = self.__longFilename
            # Otherwise use the short filename
            if filename is None:
                filename = self.__shortFilename
            # Otherwise just make something up!
            if filename is None:
                filename = 'UnknownFilename ' + \
                           ''.join(random.choice(string.ascii_uppercase + string.digits)
                                   for _ in range(5)) + '.bin'

        if customPath is not None and customPath != '':
            if customPath[-1] != '/' or customPath[-1] != '\\':
                customPath += '/'
            # if unique_id is not None:
            #     filename = customPath + str(unique_id) + "_" + filename
            # else:    
            filename = customPath + filename

        print("######filename::{}", filename)    
            
        if self.__type == "data":
            """
            Write to local system
            """
            if not save_to_object_storage:
                with open(filename, 'wb') as f:
                    f.write(self.__data)
            else:                    
                """
                Write to Object Storage
                """
                tmp_file_name, file_extension = os.path.splitext(filename)

                print("######msg_document_id::{}", msg_document_id)   
                object_storage_key = object_storage_key_prefix + "/" + str(msg_id)  + "/" + (msg_document_id + "_" + filename)
                print("object_storage_bucket_name: {}: object_storage_key: {} ".format(object_storage_bucket_name, object_storage_key))    
                
                # Write attachments to the object storage                
                return_val = cosutils.save_file (object_storage_bucket_name, object_storage_key, self.__data)
                if return_val is "SUCCESS":
                    print("File Uploaded to object storage successfully")
                
                # create entries in DB2
                db_conn = db2utils.get_connection()
                print("db_conn: {}".format(db_conn))
                sql = f'''SELECT ID FROM FINAL TABLE (INSERT INTO EVERESTSCHEMA.EVRE_LEARNING_EMAIL_ATTACHMENTS (EVRE_EMAIL_MSG_ID, 
                            DOCUMENT_NAME, DOCUMENT_TYPE, CLASSIFICATION_TYPE, STATUS) 
                            VALUES ({msg_id},                                  
                                '{object_storage_key}',
                                '{file_extension}',
                                'N/A',
                                'N') 
                            )       
                            '''
                # print ("sql: {}".format(sql))

                stmt = ibm_db.exec_immediate(db_conn, sql)
                result = ibm_db.fetch_both(stmt)
                attachment_id = None
                if result:
                    attachment_id = result["ID"]
                
                print(f'attachment_id: {attachment_id}')

        else:
            self.saveEmbededMessage(contentId, json, useFileName, raw, customPath, customFilename)
        return filename

    def saveEmbededMessage(self, contentId=False, json=False, useFileName=False, raw=False, customPath=None,
                           customFilename=None):
        self.data.save(json, useFileName, raw, contentId, customPath, customFilename)

    @property
    def cid(self):
        """
        Returns the content ID of the attachment, if it exists.
        """
        return self.__cid

    contend_id = cid

    @property
    def data(self):
        """
        Returns the attachment data.
        """
        return self.__data

    @property
    def dir(self):
        """
        Returns the directory inside the msg file where the attachment is located.
        """
        return self.__dir

    @property
    def longFilename(self):
        """
        Returns the long file name of the attachment, if it exists.
        """
        return self.__longFilename

    @property
    def msg(self):
        """
        Returns the Message instance the attachment belongs to.
        """
        return self.__msg

    @property
    def props(self):
        """
        Returns the Properties instance of the attachment.
        """
        return self.__props

    @property
    def shortFilename(self):
        """
        Returns the short file name of the attachment, if it exists.
        """
        return self.__shortFilename

    @property
    def type(self):
        """
        Returns the type of the data.
        """
        return self.__type