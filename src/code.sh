#!/bin/bash

function main() {
    set -e -x -o pipefail   # Output each line as executed, exit bash upon error

    # TODO get project ID using the command line
    project_id=$DX_PROJECT_CONTEXT_ID

    output_location=/home/dnanexus/out
    csv_out=${output_location}/csv/duty_csv
    html_out=${output_location}/html/duty_csv
    logfile_out=${output_location}/logfile/duty_csv
    echo $output_location

    dx-download-all-inputs --parallel

    # Create input and output dirs
    mkdir -p ${csv_out} ${html_out} ${logfile_out}

    docker_fileid='project-GPpBzYj04jvJ5B8GPkVp25xB:file-GQ8xxFj04jv88VXvGVQ651Qp'
    dx download ${docker_fileid}
    # Get name of docker file (should include the version) and name of image
    docker_filename=$(dx describe ${docker_fileid} --name)
    # --force-local required as if tarfile name contains a colon it tries to resolve the tarfile to a machine name
    docker_imagename=$(tar xfO "${docker_filename}" manifest.json --force-local | sed -E 's/.*"RepoTags":\["?([^"]*)"?.*/\1/')
    docker load < "${docker_filename}"  # Load docker image
    sudo docker images

    # Get secrets
    amazon_email_username=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:file-GFBj2B80Z0gQkgxp31v1Qjpk)
    amazon_email_password=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:file-GFBj2vj0Z0gg64F222p5PQzk)
    DNAnexus_auth_token=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:file-GB8PPx00Z0gxq9xbFkZz2q69)

    docker run -e DX_API_TOKEN=${DNAnexus_auth_token} -v /data/:/data/ -v ${output_location}:/outputs/ "${docker_imagename}" -P ${project_name} -I ${project_id} -EU ${amazon_email_username} -PW ${amazon_email_password} -TP ${tso_pannumbers//,/ } -SP ${stg_pannumbers//,/ } -CP ${cp_capture_pannos//,/ } -T ${testing}

    # Move outputs into their respective output folders to delocalise into the dnanexus project
    mv ${output_location}/*.log ${logfile_out}
    mv ${output_location}/*.html ${html_out}

    if find "${output_location}" -name "*.csv";
        then
            mv ${output_location}/*.csv ${csv_out}
    fi
    
    dx-upload-all-outputs --parallel
}
