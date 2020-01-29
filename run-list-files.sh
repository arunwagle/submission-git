ibmcloud fn action get --summary /OSNorth.Arun.Wagle.Org_FastStart/submission_intake/list_files
ibmcloud fn action invoke --blocking --result /OSNorth.Arun.Wagle.Org_FastStart/submission_intake/list_files --param ''

ibmcloud fn action invoke --blocking --result /OSNorth.Arun.Wagle.Org_FastStart/submission_intake/extract_email_msgs --param {"cos_everest_submission_bucket": "everest-submission-bucket",  "object_id": 43 }

ibmcloud fn action invoke /OSNorth.Arun.Wagle.Org_FastStart/submission_intake/extract_email_msgs --result --param {"cos_everest_submission_bucket": "everest-submission-bucket",  "object_id": 43 }