#!/bin/bash
# Automate_duty_v2.0.0
# The following line causes bash to exit at any point if there is any error
# and to output each line as it is executed -- useful for debugging
set -e -x -o pipefail
### Set up parameters
# Location of the Automate_Duty docker file
docker_file=project-GF8f8100BVpKbp1G9Fx3bkJk:file-GFF90jj0BVpF7078Gx9723b2
#DNAnexus_project_ID
DNAnexus_project_id=$DNAnexus_Project_ID
# Project type. Options are WES, SNP, MokaPipe and TSO500
project_type=$project_type
#Amazon email server userane and password
amazon_email_username=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_username)
amazon_email_password=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_password)
#read the DNA Nexus api key as a variable
DNAnexus_auth_token=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:DNAnexus_read_only_auth_token)
# make folder to hold downloaded files
echo $DNAnexus_project_id
echo $project_type
echo $amazon_email_username
echo $amazon_email_password
echo $DNAnexus_auth_token
#mkdir to_test
# cd to test dir
# download the docker file from 001_Tools...(after testing)
dx download $docker_file --auth "${DNAnexus_auth_token}"
docker load -i '/home/dnanexus/automate_duty_v2.tgz'
#mark-section "Run the python script"
# docker run - mount the home directory as a share
docker run automate_duty:v2.0.0 \
    --project_id=$DNAnexus_project_id \
    --proj_type=$project_type \
    --amazon_username=$amazon_email_username \
    --amazon_password=$amazon_email_password \
    --DNAnexus_token=$DNAnexus_auth_token
