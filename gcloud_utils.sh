#!/bin/bash


ACTION=${1:-auth-login}


# ===== USER INPUTS =====
REGION=us-east1
SERVICE_NAME=market-audience-predictions
APP_SOURCE=notebooks/06-app
# ========== X ==========

PRIVATE_KEY_FILEPATH=$(find $HOME/gcp_keys/$SERVICE_ACCOUNT_NAME/ -name "*$GCP_PROJECT_ID*" -printf "%s\t%p\n" | sed 's/^.\{5\}//')
SERVICE_ACCOUNT=$SERVICE_ACCOUNT_NAME@$GCP_PROJECT_ID.iam.gserviceaccount.com


if [[ "$ACTION" == 'auth-login' ]]; then
    gcloud auth login --cred-file=$PRIVATE_KEY_FILEPATH --project=$GCP_PROJECT_ID
    echo "Acivated service account"
elif [[ "$ACTION" == 'run-deploy' ]]; then
    gcloud run deploy \
        $SERVICE_NAME \
        --ingress=all \
        --source=$APP_SOURCE\
        --platform=managed \
        --service-account=$SERVICE_ACCOUNT \
        --cpu=2 \
        --memory=2Gi \
        --port=8502 \
        --region=$REGION \
        --allow-unauthenticated \
        --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID" \
        --quiet
elif [[ "$ACTION" == 'run-delete' ]]; then
    gcloud artifacts repositories delete \
        cloud-run-source-deploy \
        --location=$REGION \
        --quiet
    gcloud run services delete $SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --quiet
    gcloud storage rm --recursive gs://${GCP_PROJECT_ID}_cloudbuild/ --quiet
fi
