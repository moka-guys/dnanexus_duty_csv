#!/bin/bash

function main() {
    set -e -x -o pipefail   # Output each line as executed, exit bash on error

    dx-download-all-inputs --parallel

    # Get secrets
    AMAZON_U=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_username)
    AMAZON_PW=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:amazon_email_server_password)
    AUTH_TOKEN=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:mokaguys_nexus_auth_key)

    # Get project ID from project name
    if (dx find projects --auth "${AUTH_TOKEN}" | grep "${project_name}");
        then
            echo "Project $project_name exists"
            PROJ_ID=$(dx find projects --auth "${AUTH_TOKEN}" | grep "${project_name}" | grep -Eo '^\S*')
        else
            echo "Project $project_name does not exist"
            exit 1
    fi

    OUTDIR=/home/dnanexus/out
    CSV_OUTDIR="${OUTDIR}/csv/duty_csv"
    HTML_OUTDIR="${OUTDIR}/html/duty_csv"
    TXT_OUTDIR="${OUTDIR}/txt/duty_csv"
    LOGFILE_OUTDIR="${OUTDIR}/logfile/duty_csv"
    
    mkdir -p $CSV_OUTDIR $HTML_OUTDIR $LOGFILE_OUTDIR $TXT_OUTDIR # Create in and out dirs

    DOCKER_FILEID='project-ByfFPz00jy1fk6PjpZ95F27J:file-Gp74Jp00jy1v1ZjP0pyBB05f'
    dx download $DOCKER_FILEID
    DOCKER_FILENAME=$(dx describe $DOCKER_FILEID --name)
    # --force-local required as if tarfile name contains a colon it tries to resolve the tarfile to a machine name
    DOCKER_IMAGENAME=$(tar xfO "${DOCKER_FILENAME}" manifest.json --force-local | sed -E 's/.*"RepoTags":\["?([^"]*)"?.*/\1/')
    docker load < "$DOCKER_FILENAME"  # Load docker image
    sudo docker images

    DOCKER_CMD="docker run -e DX_API_TOKEN=$AUTH_TOKEN -v /data/:/data/ -v $OUTDIR:/outputs/ $DOCKER_IMAGENAME -P $project_name -I $PROJ_ID -EU $AMAZON_U -PW $AMAZON_PW -TP $tso_pannumbers  -SP $stg_pannumbers  -CP $cp_capture_pannos"

    if [ "${testing}" == true ];
        then
            DOCKER_CMD+=" -T"
    fi

    eval "${DOCKER_CMD}"

    # Move outputs into output folders to delocalise into dnanexus project
    mv ${OUTDIR}/*.log $LOGFILE_OUTDIR
    mv ${OUTDIR}/*.html $HTML_OUTDIR

    declare -A dir_dict
    dir_dict=( [".csv"]="$CSV_OUTDIR" [".txt"]="$TXT_OUTDIR" )

    for filetype in "${!dir_dict[@]}"; do
        if compgen -G "${OUTDIR}/*${filetype}" > /dev/null; then  # If file exists (i.e. run has files requiring download)
            mv ${OUTDIR}/*${filetype} ${dir_dict[$filetype]}
        fi
    done

    dx-upload-all-outputs --parallel
}
