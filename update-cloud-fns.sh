# Create the list_files action
#ibmcloud fn action create submission_intake/list_files --kind python:3.7 fn_list_files.zip 
ibmcloud fn action update submission_intake/list_files --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 120000 --web true -a web-custom-options false submission/ibm_cloud_functions/fn_list_files/list_files.py 

#ibmcloud fn action create submission_intake/extract_email_msgs --kind python:3.7 --timeout 120000 fn_extract_email_msgs.zip 
ibmcloud fn action update submission_intake/extract_email_msgs --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 120000 --web true -a web-custom-options false submission/ibm_cloud_functions/fn_extract_email_msgs/extract_email_msgs.py 

#ibmcloud fn action create submission_intake/doc_converto_pdf --kind python:3.7 --timeout 120000 fn_doc_converto_pdf.zip 
ibmcloud fn action update submission_intake/doc_converto_pdf --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 120000 --web true -a web-custom-options false submission/ibm_cloud_functions/fn_doc_converto_pdf/doc_convert_to_pdf.py 

#ibmcloud fn action create submission_intake/fn_split_pdf --kind python:3.7 --timeout 120000 fn_split_pdf.zip 
ibmcloud fn action update submission_intake/split_pdf --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 300000 --web true -a web-custom-options false submission/ibm_cloud_functions/fn_split_pdf/split_pdf.py 

#ibmcloud fn action create submission_intake/doc_converto_txt --kind python:3.7 --timeout 120000 fn_doc_converto_txt.zip 
ibmcloud fn action update submission_intake/doc_converto_txt --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 300000 --web true -a web-custom-options false submission/ibm_cloud_functions/fn_doc_converto_txt/doc_convert_to_txt.py 