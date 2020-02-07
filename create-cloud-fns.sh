### Create Package & Cloud functions

# List system packages
ibmcloud fn package list /whisk.system

# Create packages
ibmcloud fn package create submission_intake

# This method is not used, docker image is created to deploy build files
# 1.. create a zip for source code
# zip -j fn_list_files.zip  submission/ibm_cloud_functions/fn_list_files/__main__.py
# zip -r fn_list_files.zip  submission/utils/*.py

# # 2.. 
# zip -j fn_extract_email_msgs.zip  submission/ibm_cloud_functions/fn_extract_email_msgs/__main__.py
# zip -r fn_extract_email_msgs.zip  submission/utils/*.py


# # 3.. 
# zip -j fn_doc_converto_pdf.zip  submission/ibm_cloud_functions/fn_doc_converto_pdf/__main__.py
# zip -r fn_doc_converto_pdf.zip  submission/utils/*.py

# # 4.. 
# zip -j fn_doc_converto_txt.zip  submission/ibm_cloud_functions/fn_doc_converto_txt/__main__.py
# zip -r fn_doc_converto_txt.zip  submission/utils/*.py

# # 5.. 
# zip -j fn_split_pdf.zip  submission/ibm_cloud_functions/fn_split_pdf/__main__.py
# zip -r fn_split_pdf.zip  submission/utils/*.py

# Create the list_files action
#ibmcloud fn action create submission_intake/list_files --kind python:3.7 fn_list_files.zip 
ibmcloud fn action create submission_intake/list_files --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 120000 submission/ibm_cloud_functions/fn_list_files/list_files.py 

#ibmcloud fn action create submission_intake/extract_email_msgs --kind python:3.7 --timeout 120000 fn_extract_email_msgs.zip 
ibmcloud fn action create submission_intake/extract_email_msgs --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 120000 submission/ibm_cloud_functions/fn_extract_email_msgs/extract_email_msgs.py 

#ibmcloud fn action create submission_intake/doc_converto_pdf --kind python:3.7 --timeout 120000 fn_doc_converto_pdf.zip 
ibmcloud fn action create submission_intake/doc_converto_pdf --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 120000 submission/ibm_cloud_functions/fn_doc_converto_pdf/doc_convert_to_pdf.py 

#ibmcloud fn action create submission_intake/fn_split_pdf --kind python:3.7 --timeout 120000 fn_split_pdf.zip 
ibmcloud fn action create submission_intake/split_pdf --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 300000 submission/ibm_cloud_functions/fn_split_pdf/split_pdf.py 

#ibmcloud fn action create submission_intake/doc_converto_txt --kind python:3.7 --timeout 120000 fn_doc_converto_txt.zip 
ibmcloud fn action create submission_intake/doc_converto_txt --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake_8 --timeout 300000 submission/ibm_cloud_functions/fn_doc_converto_txt/doc_convert_to_txt.py 



