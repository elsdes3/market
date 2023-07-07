#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to authenticate with BigQuery."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument

import os
from glob import glob
from typing import Dict

from google.oauth2 import service_account


def auth_to_bigquery(sec_key_data_dir: os.PathLike) -> Dict[str, str]:
    """."""
    gcp_proj_id = os.environ["GCP_PROJECT_ID"]
    gcp_creds_fpath = glob(os.path.join(sec_key_data_dir, "*", "*.json"))
    # if os.path.exists(gcp_creds_fpath):
    #     gcp_creds = service_account.Credentials.from_service_account_file(
    #         gcp_creds_fpath
    #     )
    if gcp_creds_fpath and os.path.exists(gcp_creds_fpath[0]):
        print(gcp_creds_fpath[0])
        gcp_creds = service_account.Credentials.from_service_account_file(
            gcp_creds_fpath[0]
        )
    else:
        gcp_creds = None
    gcp_auth_dict = dict(gcp_project_id=gcp_proj_id, gcp_creds=gcp_creds)
    return gcp_auth_dict
