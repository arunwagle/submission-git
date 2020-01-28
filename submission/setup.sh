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


# 1.. create a zip for source code
zip -j tp-risk-create-new-request.zip  create-new-request/__main__.py
zip -j -r tp-risk-create-new-request.zip  ../../utils/app_enums.py ../../framework/db2_settings.py

# 2.. create a zip for source code
zip -j fn_list_files.zip  list_files/__main__.py
zip -j -r list_files.zip  ../../utils/app_enums.py ../../framework/db2_settings.py

# 3.. create a zip for source code
zip -j tp-risk-get-matched-entities.zip  get-matched-entities/__main__.py
zip -j -r tp-risk-get-matched-entities.zip  ../../utils/app_enums.py ../../framework/db2_settings.py

# 4. Create watson discovery news extractor
zip -j ex-watson-discovery-news.zip  watson-discovery-news/__main__.py



# Create the submitRequest action
ibmcloud fn action create tp-risk-analytics/create-new-request --kind python:3.7 tp-risk-create-new-request.zip
ibmcloud fn action create tp-risk-analytics/save-user-search --kind python:3.7 tp-risk-save-user-search.zip
ibmcloud fn action create tp-risk-analytics/get-matched-entities --kind python:3.7 tp-risk-get-matched-entities.zip

# Deploy Extractor specific actions
ibmcloud fn action create extractors/watson-discovery-news --kind python:3.7 ex-watson-discovery-news.zip

# Update Actions
ibmcloud fn action update tp-risk-analytics/create-new-request --kind python:3.7 tp-risk-create-new-request.zip
ibmcloud fn action update tp-risk-analytics/save-user-search --kind python:3.7 tp-risk-save-user-search.zip
ibmcloud fn action update tp-risk-analytics/get-matched-entities --kind python:3.7 tp-risk-get-matched-entities.zip

# Deploy Extractor specific actions
ibmcloud fn action update extractors/watson-discovery-news --kind python:3.7 ex-watson-discovery-news.zip


# Create a sequence.
ibmcloud fn action create tp-risk-analytics/assess-risk-sequence --sequence tp-risk-analytics/create-new-request,extractors/watson-discovery-news




# Cloud function Object Storage
#ibmcloud fn service bind cloud-object-storage cloud-object-storage




# Bind the service credentials to the action
#ibmcloud fn service bind dashDB collectStats --instance ghstatsDB --keyname ghstatskey

# Create a trigger for firing off daily at 6am
#ibmcloud fn trigger create myDaily --feed /whisk.system/alarms/alarm --param cron "0 6 * * *" --param startDate "2018-03-21T00:00:00.000Z" --param stopDate "2018-12-31T00:00:00.000Z"

# Create a rule to connect the trigger with the action
#ibmcloud fn rule create myStatsRule myDaily collectStats



ibmcloud fn action get --summary /OSNorth.Arun.Wagle.Org_BBAndT/riskAnalytics/newRequest
ibmcloud fn action invoke --blocking --result /OSNorth.Arun.Wagle.Org_BBAndT/riskAnalytics/newRequest --param place Ork

