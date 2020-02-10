#### Docker deployment steps

### Step 1 - Update Dockerfile in PROJECT_ROOT/submission_docker
### Step 2 Build docker image. Make sure the tag name is changed after each new modifications
### Step3 Push the docker image to the docker repo
# https://hub.docker.com/repository/docker/arunwagle123/ibm_cloudfunctions_repo/tags?page=1

docker build --pull --no-cache -t arunwagle123/ibm_cloudfunctions_repo:submission_intake_9 .

docker push arunwagle123/ibm_cloudfunctions_repo:submission_intake_9
