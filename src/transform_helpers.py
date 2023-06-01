#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to transform raw data."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument

import os
from typing import Dict, List, Union

import pandas as pd

import categorical_helpers as ch
import sql_helpers as sq


def set_datatypes(df: pd.DataFrame, dtypes: Dict) -> pd.DataFrame:
    """Set DataFrame datatypes using dictionary."""
    df = df.astype(dtypes)
    return df


def drop_duplicates(df: pd.DataFrame, subset: List[str]) -> pd.DataFrame:
    """Drop duplicates."""
    df = df.drop_duplicates(subset=subset, keep="first")
    print(
        f"Got {len(df):,} rows and {df.shape[1]:,} columns "
        "after dropping duplicates"
    )
    return df


def map_columns(df: pd.DataFrame, mapper_dict: Dict) -> pd.DataFrame:
    """Map values in DataFrame column using dictionary."""
    for k, v in mapper_dict.items():
        df[k] = df[k].map(v)
    return df


def shuffle_data(df: pd.DataFrame) -> pd.DataFrame:
    """Shuffle data."""
    df = df.sample(frac=1.0, random_state=88)
    return df


def extract_data(query: str, gcp_auth_dict: Dict) -> pd.DataFrame:
    """Retrieve data from Google BigQuery dataset."""
    df = sq.run_sql_query(query, **gcp_auth_dict, show_df=False)
    return df


def transform_data(
    df: pd.DataFrame,
    datatypes_dict: Dict,
    duplicate_cols: List[str],
    column_mapper_dict: Dict[int, str],
    categoricals: List[str] = [],
) -> List[Union[pd.DataFrame, List[Dict]]]:
    """Transform features in data."""
    df, cat_mapper_dicts = (
        df.pipe(set_datatypes, datatypes_dict)
        .pipe(drop_duplicates, duplicate_cols)
        .pipe(map_columns, column_mapper_dict)
        .pipe(ch.cast_categoricals_as_ints, categoricals)
    )
    print(f"Transformed data has {len(df):,} rows & {df.shape[1]:,} columns")
    return [df, cat_mapper_dicts]


def create_combined_validation_data(
    df_train: pd.DataFrame, df_val: pd.DataFrame, datatypes_dict: Dict
) -> List[pd.DataFrame]:
    """Extract training & combined training+validation data for validation."""
    df_train_val = pd.concat(
        [
            df_train.assign(split="train").pipe(shuffle_data),
            df_val.assign(split="val"),
        ]
    ).pipe(set_datatypes, datatypes_dict)
    df_train = df_train_val.query("split == 'train'")
    df_train, df_train_val = [
        df.drop(columns=["split"]) for df in [df_train, df_train_val]
    ]
    return [df_train, df_train_val]


def load_data(
    df: pd.DataFrame, processed_data_dir: str, split_type: str = "train"
) -> None:
    """Save data to file on local disk."""
    fpath = os.path.join(
        processed_data_dir, f"{split_type}_processed.parquet.gzip"
    )
    df.to_parquet(fpath, index=False, compression="gzip", engine="pyarrow")
    print(f"Exported data to {fpath}")
