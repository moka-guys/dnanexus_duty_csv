#!/bin/bash

function main() {
    set -e -x -o pipefail   # Output each line as executed, exit bash upon error

    docker_file=project-GF8f8100BVpKbp1G9Fx3bkJk:file-GFF90jj0BVpF7078Gx9723b2
    DNAnexus_project_id=$DNAnexus_Project_ID
    project_type=$project_type

    amazon_email_username=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_username)
    amazon_email_password=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_password)
    DNAnexus_auth_token=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:DNAnexus_read_only_auth_token)

    echo $DNAnexus_project_id
    echo $project_type
    echo $amazon_email_username
    echo $amazon_email_password
    echo $DNAnexus_auth_token

    dx download $docker_file --auth "${DNAnexus_auth_token}"
    docker load -i '/home/dnanexus/automate_duty_v2.tgz'

    docker run automate_duty:v2.0.0 \
        --project_id=$DNAnexus_project_id \
        --proj_type=$project_type \
        --amazon_username=$amazon_email_username \
        --amazon_password=$amazon_email_password \
    --DNAnexus_token=$DNAnexus_auth_token
}
