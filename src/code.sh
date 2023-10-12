#!/bin/bash

function main() {
    set -e -x -o pipefail   # Output each line as executed, exit bash on error

    dx-download-all-inputs --parallel

    # Get secrets
    AMAZON_U=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_username)
    AMAZON_PW=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_password)
    AUTH_TOKEN=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:mokaguys_nexus_auth_key)

    # Get project ID form project name
    if (dx find projects --auth $AUTH_TOKEN | grep $project_name);
        then
            echo "Project $project_name exists"
            PROJ_ID=$(dx find projects --auth $AUTH_TOKEN | grep $project_name | grep -Eo '^\S*')
        else
            echo "Project $project_name does not exist"
            exit 1
    fi

    OUTDIR=/home/dnanexus/out
    CSV_OUTDIR=${OUTDIR}/csv/duty_csv
    HTML_OUTDIR=${OUTDIR}/html/duty_csv
    LOGFILE_OUTDIR=${OUTDIR}/logfile/duty_csv
    
    mkdir -p $CSV_OUTDIR $HTML_OUTDIR $LOGFILE_OUTDIR # Create in and out dirs

    DOCKER_FILEID='project-ByfFPz00jy1fk6PjpZ95F27J:file-GZY9vFj0jy1q7vKz2x2KvqBG'
    dx download $DOCKER_FILEID
    DOCKER_FILENAME=$(dx describe $DOCKER_FILEID --name)
    # --force-local required as if tarfile name contains a colon it tries to resolve the tarfile to a machine name
    DOCKER_IMAGENAME=$(tar xfO $DOCKER_FILENAME manifest.json --force-local | sed -E 's/.*"RepoTags":\["?([^"]*)"?.*/\1/')
    docker load < "$DOCKER_FILENAME"  # Load docker image
    sudo docker images

    # Turn comma separated strings into space separated strings
    CP_CAP_PANNOS=${cp_capture_pannos//,/ }
    STG_PANNOS=${stg_pannumbers//,/ }
    TSO_PANNOS=${tso_pannumbers//,/ }

    DOCKER_CMD="docker run -e DX_API_TOKEN=$AUTH_TOKEN -v /data/:/data/ -v $OUTDIR:/outputs/ $DOCKER_IMAGENAME -P $project_name -I $PROJ_ID -EU $AMAZON_U -PW $AMAZON_PW -TP $TSO_PANNOS  -SP $STG_PANNOS  -CP $CP_CAP_PANNOS"

    if [ "$testing" == true ];
        then
            DOCKER_CMD+=" -T"
    fi

    eval $DOCKER_CMD

    # Move outputs into output folders to delocalise into dnanexus project
    mv ${OUTDIR}/*.log $LOGFILE_OUTDIR
    mv ${OUTDIR}/*.html $HTML_OUTDIR

    if compgen -G "$OUTDIR/*.csv" > /dev/null;  # If CSV exists
        then
            mv ${OUTDIR}/*.csv $CSV_OUTDIR
    fi
    
    dx-upload-all-outputs --parallel
}
