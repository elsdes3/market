#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to transform raw data."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments

from typing import Dict

import pandas as pd

import src.sql.sql_helpers as sq


def set_datatypes(df: pd.DataFrame, dtypes: Dict) -> pd.DataFrame:
    """Set DataFrame datatypes using dictionary."""
    df = df.astype(dtypes)
    return df


def map_columns(df: pd.DataFrame, mapper_dict: Dict) -> pd.DataFrame:
    """Map values in DataFrame column using dictionary."""
    for k, v in mapper_dict.items():
        df[k] = df[k].map(v)
    return df


def extract_data(query: str, gcp_auth_dict: Dict) -> pd.DataFrame:
    """Retrieve data from Google BigQuery dataset."""
    df = sq.run_sql_query(query, **gcp_auth_dict)
    return df
