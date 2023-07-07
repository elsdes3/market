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
    elif [[ "$ACTION" == 'reset-train' ]]; then
        cd 02-train
    elif [[ "$ACTION" == 'reset-explore' ]]; then
        cd 03-explore
    elif [[ "$ACTION" == 'reset-upload' ]]; then
        cd 04-upload
    elif [[ "$ACTION" == 'reset-dash' ]]; then
        cd 05-dash
    elif [[ "$ACTION" == 'reset-app' ]]; then
        cd 06-app
    else
        cd 07-cleanup
    fi

    if [[ "$ACTION" -ne 'reset-app' ]]; then
        cd notebooks
        rm -rf .ipynb_checkpoints/

        cd ../../../src
    fi

    if [[ "$ACTION" == 'reset-app' ]]; then
        cd src/
    fi

    rm -rf __pycache__/
fi
