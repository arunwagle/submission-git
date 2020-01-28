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


ibmcloud fn action update submission_intake/list_files --kind python:3.7 --timeout 120000 fn_list_files.zip 

ibmcloud fn action update submission_intake/extract_email_msgs --kind python:3.7 --timeout 120000 fn_extract_email_msgs.zip 
ibmcloud fn action update submission_intake/extract_email_msgs --docker arunwagle123/ibm_cloudfunctions_repo:submission_intake --timeout 120000 fn_extract_email_msgs.zip

ibmcloud fn action update submission_intake/doc_converto_pdf --kind python:3.7 --timeout 120000 fn_doc_converto_pdf.zip 

ibmcloud fn action update submission_intake/doc_converto_txt --kind python:3.7 --timeout 120000 fn_doc_converto_txt.zip 

ibmcloud fn action update submission_intake/fn_split_pdf --kind python:3.7 --timeout 120000 fn_split_pdf.zip 




ibm_db_sa \
   ibm-cos-sdk \
   ibm_cloud_sdk_core==1.5.1 \
   ibm_watson \
   pandas \
   python-dateutil \
   requests \
   PyPDF2 \
   fuzzywuzzy \
   python-Levenshtein \
   extract_msg \
   --e /Users/arun.wagle@ibm.com/IBM/Demos/Watson/clients/EverestRe/submission-git/submission/distarunwagle_submission_intake_utils-0.0.1-py3-none-any.whl