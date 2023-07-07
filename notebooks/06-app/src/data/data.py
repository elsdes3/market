#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Create dashboard for client to get insights and propensity predictions."""

import io
from time import sleep
from typing import Dict, List

import pandas as pd
import streamlit as st

import src.transform.transform_helpers as th
from src.bigquery.bigquery_auth_helpers import auth_to_bigquery

# pylint: disable=line-too-long,invalid-name,abstract-class-instantiated
# pylint: disable=dangerous-default-value

CACHE_DURATION = 3_600


@st.cache_data(
    show_spinner="Preparing data that can be downloaded as .XLSX file...",
    ttl=CACHE_DURATION,
    experimental_allow_widgets=True,
)
def export_to_xlsx(dataframe: pd.DataFrame) -> None:
    """Export data with cohorts to XLSX file."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        # Write each dataframe to a different worksheet
        dataframe.to_excel(writer, sheet_name="Sheet1", index=False)
    success = st.success("Done.")
    sleep(1)
    success.empty()
    return buffer.getvalue()


@st.cache_data(
    show_spinner="Fetching data from BigQuery...", ttl=CACHE_DURATION
)
def get_data(
    query: str,
    mapper_dict: Dict[str, Dict[int, str]],
    _dtypes_dict: Dict,
    gcp_keys_dir_path: str,
    date_col: str = "",
    data_type: str = "profiles",
    custom_sort_single_col: Dict[str, List[str]] = dict(),
) -> pd.DataFrame:
    """Get data from BigQuery table."""
    gcp_authorization_dict = auth_to_bigquery(gcp_keys_dir_path)
    df = th.extract_data(query, gcp_authorization_dict)
    if mapper_dict:
        df = df.pipe(th.map_columns, mapper_dict)
    df = df.pipe(th.set_datatypes, _dtypes_dict)
    if date_col:
        df[date_col] = pd.to_datetime(df["date"], utc=False)
    if custom_sort_single_col and len(list(custom_sort_single_col)) == 1:
        col_sort = list(custom_sort_single_col)[0]
        sort_order = list(custom_sort_single_col.values())[0]
        df = df.set_index(col_sort).loc[sort_order].reset_index()
    success = st.success(
        f"Fetched {len(df):,} rows of {data_type} data from BigQuery!"
    )
    sleep(1)
    success.empty()
    return df
