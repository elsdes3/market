# Market

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/elsdes3/market)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/elsdes3/market/main/notebooks/02-train/notebooks/04_train.ipynb)
![CI](https://github.com/elsdes3/market/workflows/CI/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/mit)
![OpenSource](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![prs-welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)

## [About](#about)

Modeling visitor propensity to make purchase during return visit to the Google merchandise store, to create a marketing audience based on propensity-based groupings. This is intended to help a marketing team target high-value first-time visitors to the store's site during a one-month period with promotions through a campaign aimed at ensuring a conversion (the visitor makes a purchase) when they return to the store.

See `index.qmd` for project details.

## [Pre-Requisites](#pre-requisites)
### [Google Cloud](#google-cloud)
1. Create a Google Cloud project
2. From the BigQuery console
   - select the newly created project and create two GCP Service Accounts with the following permissions
     - used during development (raw data retrieval, analysis and dashboard)
       - *Cloud Storage Admin*
       - *BigQuery Job User*
       - *BigQuery Data Viewer*
       - *BigQuery Data Editor*
       - this is used for all notebooks (folders `01-get-data`, `02-train`, `03-explore`, `04-upload`, `05-dash`, `07-cleanup`)
     - deploying containerized dashboard to GCP Cloud Run
       - *Editor*
       - *BigQuery Data Viewer*
       - *Cloud Run Admin*
       - *Service Account User*
       - this is used for the containerized dashboard (`06-app`)
   - create access keys for both service accounts and download the keys as JSON files into the home directory (`/home/<user-name>`)
   - add the following datasets
     - publicly available GA360 dataset
       - click **+ ADD** to add the data
       - select **Star a project by name**
       - select the **data-to-insights** project
         - one of the available datasets is *ecommerce* and the data in the *web_analytics* table from this dataset will be used for this project
     - custom (personal) dataset, to which tables will be added during development
       - select the ellipses (three vertical dots)
       - click **Create dataset**
       - enter a dataset ID
       - click **CREATE DATASET**

### [Local](#local)
1. Export the following environment variables into the local shell
   - `GCP_PROJECT_ID`
     - GCP project ID
   - `SERVICE_ACCOUNT_NAME_BQ`
     - during development, set this to the name of the service account created for use in notebooks during development
   - `SERVICE_ACCOUNT_NAME_CR`
     - during deployment, set this to the name of the service account created for for manipulating Google Cloud Run resources, when deploying the containerized dashboard to Cloud Run

## [Project Organization](#project-organization)

    ├── .gitignore                    <- files and folders to be ignored by version control system
    ├── .pre-commit-config.yaml       <- configuration file for pre-commit hooks
    ├── .github
    │   ├── workflows
    │       └── main.yml              <- configuration file for CI build on Github Actions
    ├── notebooks                     <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                                    and a short `-` delimited description, e.g. `01-jqp-initial-data-exploration`.
    ├── data
    │   ├── raw                       <- raw data downloaded from public sites
    |   └── processed                 <- transformed data
    ├── docker-compose.yml            <- to containerize v2 dashboard app
    ├── LICENSE
    ├── Makefile                      <- Makefile with commands like `make lint` or `make build`
    ├── README.md                     <- The top-level README for developers using this project.
    ├── src
    │   ├── *.py                      <- custom Python modules
    ├── utils.sh                      <- Shell scripting utilities for managing Docker containers.
    ├── tox.ini                       <- tox file with settings for running tox; see https://tox.readthedocs.io/en/latest/

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
