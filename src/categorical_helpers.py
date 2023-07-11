#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to handle categorical data."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument

from functools import reduce
from typing import Dict, List, Union

import pandas as pd


def get_categorical_string_to_int_mapping(
    df: pd.DataFrame, mapper_dict: Dict, split_type: str = "train"
) -> pd.DataFrame:
    """Get str-to-int mapper dict for categorical columns as a DataFrame."""
    df = pd.DataFrame.from_records(mapper_dict).stack().reset_index(level=[1])
    df[f"len_mapper_dict_{split_type}"] = df[0].str.len()
    df = df.rename(
        columns={"level_1": "column", 0: f"mapper_dict_{split_type}"}
    )
    return df


def cast_categoricals_as_ints(
    df: pd.DataFrame, categoricals: List[str] = []
) -> List[Union[pd.DataFrame, List[Dict[str, int]]]]:
    """Cast categoricals as integers."""
    cat_mapper_dicts = []
    if categoricals:
        for cat_col in categoricals:
            cat_mapper_dict = dict(
                zip(
                    df[cat_col].cat.categories.tolist(),
                    range(df[cat_col].nunique()),
                )
            )
            df[cat_col] = (
                df[cat_col].map(cat_mapper_dict)
                # .astype(pd.Int8Dtype())
                .astype(pd.Int64Dtype())
            )
            cat_mapper_dicts.append({cat_col: cat_mapper_dict})
    return [df, cat_mapper_dicts]


def combine_categorical_str_to_int_mappers(
    mappers: List[List],
    dfs_list: List[pd.DataFrame],
    split_types: List[str] = ["train", "val", "test"],
) -> pd.DataFrame:
    """."""
    df = reduce(
        lambda left, right: pd.merge(left, right, on=["column"], how="outer"),
        [
            get_categorical_string_to_int_mapping(df, mapper_dict, stype)
            for mapper_dict, stype, df in zip(mappers, split_types, dfs_list)
        ],
    ).sort_index(axis=1)
    return df


def cast_categoricals_as_strings(
    df: pd.DataFrame, cat_mapper_dicts: List[str]
) -> List[Union[pd.DataFrame, List[Dict[str, int]]]]:
    """Cast categoricals as strings."""
    for map_dict in cat_mapper_dicts:
        for k, v in map_dict.items():
            df[k] = df[k].map({c_int: c for c, c_int in v.items()})
    return df
