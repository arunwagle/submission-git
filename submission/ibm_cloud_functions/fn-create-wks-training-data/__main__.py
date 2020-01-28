#######
#######
#######
#
#
# Written by Arun Wagle, arun.wagle

import logging, sys, json
import os
from os import walk

from submission.utils.watsondiscoveryutils import get_results_by_doc_name

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)


def main(params):
    logging.info(f'Inside create-new-request  :: params {params}')
    try:

        training_dir = params.get("training_dir", None)
        print ("training_dir:", training_dir)
        if training_dir is None or "":
            raise Exception("Please provide a directory ")
        extensions = ['.docx','.doc', 'pdf', 'pptx']
        exclude = set(["not-used-for-training"])
        for root, subFolders, files in os.walk(training_dir, topdown=False):  
            # do not process excluded directories
            [subFolders.remove(d) for d in list(subFolders) if d in exclude]                                             
            for msg_filename in files:     
                if msg_filename.endswith(tuple(extensions)) :                       
                    msg_file_path = os.path.join(root, msg_filename)
                    print ("msg_file_path: {}", msg_file_path)

    except:
        logging.error("Some error occured", e)

    return {"result": ""}


if __name__ == "__main__":
    # python3 -m submission.fn-create-wks-training-data.__main__
    param = {
        'training_dir':'/Users/arun.wagle@ibm.com/Downloads/IBMPilot20191122154632/email_attachments/training-processed'      
    }

    # p_json = json.dumps(param)

    main(param)

