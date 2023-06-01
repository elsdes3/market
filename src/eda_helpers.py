#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to transform data for exploratory data analysis."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument

from typing import List, Union

import pandas as pd


def get_class_imbalances(
    series_list: List[pd.Series],
    resampling_list: List[Union[None, str]],
    split_names: List[str],
) -> pd.DataFrame:
    """Get class imbalance for list of pandas.Series."""
    df = (
        pd.concat(
            [
                y.value_counts(normalize=True)
                .to_frame()
                .merge(
                    y.value_counts().to_frame(),
                    left_index=True,
                    right_index=True,
                    how="left",
                )
                .assign(split="train")
                .assign(resample=strategy)
                .assign(split=sname)
                for y, strategy, sname in zip(
                    series_list, resampling_list, split_names
                )
            ]
        )
        .reset_index()
        .sort_values(by=["split"])
    )
    return df


def get_feature_correlations(
    features_list: List[pd.Series],
    resampling_list: List[Union[None, str]],
    split_names: List[str],
) -> pd.DataFrame:
    """Get class imbalance for list of DataFrames."""
    df = (
        pd.concat(
            [
                (
                    X.select_dtypes(include=["float32"])
                    .corr()
                    .assign(split=sname)
                    .assign(resample=strategy)
                )
                for X, strategy, sname in zip(
                    features_list, resampling_list, split_names
                )
            ]
        )
        .reset_index()
        .rename(columns={"index": "feature"})
        .sort_values(by=["split"])
    )
    return df
