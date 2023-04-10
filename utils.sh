#!/bin/bash


ACTION=${1:-get-data}


if [[ "$ACTION" != 'reset'* ]]; then
    echo "Waiting for 5 seconds..."
    sleep 5
    echo "Done."
    docker logs -t $(docker ps --filter "name=${ACTION}" --format "{{.ID}}")
else
    docker rmi $(docker images -a --filter "reference=*${ACTION:6}*" --format "{{.ID}}")

    cd notebooks
    if [[ "$ACTION" == 'reset-get-data' ]]; then
        cd 01-get-data
    elif [[ "$ACTION" == 'reset-eda' ]]; then
        cd 02-eda
    elif [[ "$ACTION" == 'reset-transform' ]]; then
        cd 03-transform
    elif [[ "$ACTION" == 'reset-development' ]]; then
        cd 04-development
    elif [[ "$ACTION" == 'reset-post-process' ]]; then
        cd 05-post-process
    else
        cd 06-create-audience
    fi

    cd notebooks
    rm -rf .ipynb_checkpoints/

    cd ../../../src
    rm -rf __pycache__/
fi
