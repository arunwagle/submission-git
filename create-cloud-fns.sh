# Automatically set up services and actions for tutorial on
# regular Github statistics
#
# Written by Henrik Loeser


# We need to pull down the githubpy file before packaging,
# then create the zip file and thereafter delete githubpy again (or leave it?).
#
# Fetch the github module:
# wget https://raw.githubusercontent.com/michaelliao/githubpy/master/github.py
#
# Pack the action code and the github module into a zip archive
# zip -r ghstats.zip  __main__.py github.py
#
# Ok, now we can deploy the objects


# List system packages
ibmcloud fn package list /whisk.system

# Create packages
ibmcloud fn package create submission_intake

# https://cloud.ibm.com/docs/openwhisk?topic=cloud-functions-prep#prep_python_docker
docker build -t arunwagle123/ibm_cloudfunctions_repo:submission_intake .
docker push arunwagle123/ibm_cloudfunctions_repo:submission_intake
# docker pull ibmfunctions/action-python-v3.7
# docker run --rm -v "$PWD:/tmp" ibmfunctions/action-python-v3.7 bash -c "cd /tmp && virtualenv virtualenv && source virtualenv/bin/activate && pip3 install -r requirements.txt"

# 1.. create a zip for source code
zip -j fn_list_files.zip  submission/ibm_cloud_functions/fn_list_files/__main__.py
zip -r fn_list_files.zip  submission/utils/*.py

# 2.. 
zip -j fn_extract_email_msgs.zip  submission/ibm_cloud_functions/fn_extract_email_msgs/__main__.py
zip -r fn_extract_email_msgs.zip  submission/utils/*.py
# zip -r fn_extract_email_msgs.zip virtualenv

# 3.. 
zip -j fn_doc_converto_pdf.zip  submission/ibm_cloud_functions/fn_doc_converto_pdf/__main__.py
zip -r fn_doc_converto_pdf.zip  submission/utils/*.py

# 4.. 
zip -j fn_doc_converto_txt.zip  submission/ibm_cloud_functions/fn_doc_converto_txt/__main__.py
zip -r fn_doc_converto_txt.zip  submission/utils/*.py

# 5.. 
zip -j fn_split_pdf.zip  submission/ibm_cloud_functions/fn_split_pdf/__main__.py
zip -r fn_split_pdf.zip  submission/utils/*.py

# Create the list_files action
ibmcloud fn action create submission_intake/list_files --kind python:3.7 fn_list_files.zip 

ibmcloud fn action create submission_intake/extract_email_msgs --kind python:3.7 --timeout 120000 fn_extract_email_msgs.zip 
ibmcloud fn action create submission_intake/extract_email_msgs --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake --timeout 120000 fn_extract_email_msgs.zip

ibmcloud fn action create submission_intake/doc_converto_pdf --kind python:3.7 --timeout 120000 fn_doc_converto_pdf.zip 

ibmcloud fn action create submission_intake/doc_converto_txt --kind python:3.7 --timeout 120000 fn_doc_converto_txt.zip 

ibmcloud fn action create submission_intake/fn_split_pdf --kind python:3.7 --timeout 120000 fn_split_pdf.zip 






