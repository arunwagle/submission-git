import logging
import os
from os import walk
import shutil
import glob
import json
from PyPDF2 import PdfFileReader, PdfFileWriter

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s'
)


def main(params):
    logging.info('Calling fn_split_pdf.')
    training_dir = "/Users/arun.wagle@ibm.com/Downloads/training/split-doc-pdf/temp"
    
    extensions = ['pdf']
    for root, subFolders, files in os.walk(training_dir, topdown=False):  
            # do not process excluded directories  
            #           
            for filename in files:     
                if filename.endswith(tuple(extensions)) :                       
                    file_path = os.path.join(root, filename)
                    print ("file_path: {}", file_path)
                    fname = os.path.splitext(os.path.basename(file_path))[0]
                    dir_name = os.path.dirname(file_path)
                    print('dir name: {}'.format(dir_name))
                    print('fname: {}'.format(fname))
                    
                    # read pdf
                    pdf = PdfFileReader(file_path)
                    page1 = pdf.getPage(0)
                    # print(page1.extractText())
                    
                    for page in range(pdf.getNumPages()):
                        pdf_writer = PdfFileWriter()
                        pdf_writer.addPage(pdf.getPage(page))
                        split_output_dir= dir_name + "/split/" + fname
                        os.makedirs(split_output_dir, exist_ok=True)
                        output_filename = '{}/{}_page_{}.pdf'.format(split_output_dir, fname, page+1)
                        with open(output_filename, 'wb') as out:
                            pdf_writer.write(out)

                        print('Created: {}'.format(output_filename))

    return {"result": "dd"}


if __name__ == "__main__":
    # python3 -m submission.ibm_cloud_functions.fn_split_pdf.__main__
    param = {
        'cos_everest_submission_bucket': 'everest-submission-bucket',
        'final_pdf_folder': 'final_pdf',
        'document_id':'43' ,
        'submissions_data_folder':'submission_documents_data' ,
        'mode':'runtime'
    }

    # p_json = json.dumps(param)

    main(param)
