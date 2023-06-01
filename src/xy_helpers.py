#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to extract features and label."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,too-many-arguments,unused-argument

from typing import List, Union

import pandas as pd


def get_Xy(
    df: pd.DataFrame, label: str
) -> List[Union[pd.DataFrame, pd.Series]]:
    """Separate features from label."""
    X = df.drop(columns=[label])
    y = df[label]
    return [X, y]


def get_feats_label(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_train_val: pd.DataFrame,
    df_train_val_eval: pd.DataFrame,
    df_test: pd.DataFrame,
    df: pd.DataFrame,
    cols_to_drop: List[str],
    label: str,
) -> List[Union[pd.DataFrame, pd.Series]]:
    """."""
    # validation
    X_train, y_train = get_Xy(df_train, label)
    X_val, y_val = get_Xy(df_val, label)
    X_train_val, y_train_val = get_Xy(df_train_val, label)

    # evaluation
    X_train_val_eval, y_train_val_eval = get_Xy(df_train_val_eval, label)
    X_test, y_test = get_Xy(df_test, label)

    # inference
    X, y = get_Xy(df, label)

    # drop unwanted columns
    X_train = X_train.drop(columns=cols_to_drop)
    X_val = X_val.drop(columns=cols_to_drop)
    X_train_val = X_train_val.drop(columns=cols_to_drop)
    X_train_val_eval = X_train_val_eval.drop(columns=cols_to_drop)
    X_test = X_test.drop(columns=cols_to_drop)
    X = X.drop(columns=cols_to_drop)
    return [
        X_train,
        y_train,
        X_val,
        y_val,
        X_train_val,
        y_train_val,
        X_train_val_eval,
        y_train_val_eval,
        X_test,
        y_test,
        X,
        y,
    ]
