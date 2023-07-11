#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to preprocess features for ML."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments

from typing import Dict, List, Union

import pandas as pd
from imblearn.pipeline import Pipeline

import categorical_helpers as ch


def preprocess_data(
    pipe_resample: Pipeline,
    pipe_trans: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    categorical_features: List[str],
    categorical_feats_mapper_dicts: List[Dict[str, Dict[str, int]]],
) -> List[Union[pd.DataFrame, pd.Series, Pipeline]]:
    """Run feature preprocessing."""
    # perform undersampling
    if list(pipe_resample.named_steps)[0] == "us":
        X_train, y_train = pipe_resample.fit_resample(X_train, y_train)

    # change integers in categoricals back to strings
    X_train = X_train.pipe(
        ch.cast_categoricals_as_strings, categorical_feats_mapper_dicts
    )

    # train feature preprocessor
    _ = pipe_trans.fit(X_train)

    # extract numerical and categorical feature names in trained preprocessor
    # - identical to get_transformed_features()
    numericals_processed = (
        pipe_trans.named_steps["preprocessor"]
        .named_transformers_["num"]
        .named_steps["aboveavg"]
        .get_feature_names_out()
    )
    rarecats_bucket_features_out = [
        c.split("__")[-1] for c in categorical_features
    ]
    categoricals_processed = (
        pipe_trans.named_steps["preprocessor"]
        .named_transformers_["cat"]
        .named_steps["dummy"]
        .get_feature_names_out(rarecats_bucket_features_out)
        .tolist()
    )
    categoricals_processed = [
        c.replace(f"{cat_col}_", f"{cat_col}__")
        for c in categoricals_processed
        for cat_col in categorical_features
        if c.startswith(cat_col)
    ]

    # extract numerical and categorical feature names in selected features
    feats_selected = pipe_trans.named_steps["select"].get_feature_names_out(
        numericals_processed + categoricals_processed
    )
    cats_selected = [c for c in categoricals_processed if c in feats_selected]
    nums_selected = [c for c in numericals_processed if c in feats_selected]

    # get feature datatypes in selected features
    processed_dtypes = dict(
        zip(
            feats_selected,
            # [pd.Float32Dtype() for _ in nums_selected]
            # + [pd.Int8Dtype() for _ in cats_selected],
            [pd.Float64Dtype() for _ in nums_selected]
            + [pd.Int64Dtype() for _ in cats_selected],
        )
    )

    # preprocess training data
    # - identical to transform_data()
    X_train_preprocessed = pipe_trans.transform(X_train)
    X_train_preprocessed = X_train_preprocessed.rename(
        columns=dict(zip(list(X_train_preprocessed), feats_selected))
    ).astype(processed_dtypes)

    # preprocess unseen (validation or test) data
    # - identical to transform_data()
    X_val_preprocessed = pipe_trans.transform(X_val)
    X_val_preprocessed = X_val_preprocessed.rename(
        columns=dict(zip(list(X_val_preprocessed), feats_selected))
    ).astype(processed_dtypes)

    # perform oversampling
    if list(pipe_resample.named_steps)[0] == "os":
        X_train, y_train = pipe_resample.fit_resample(
            X_train_preprocessed, y_train
        )
    return [X_train_preprocessed, y_train, X_val_preprocessed, pipe_trans]


def get_transformed_features(
    pipe: Pipeline,
    num_last_step: str,
    pipe_last_step: str,
    categorical_features: List[str],
) -> List[Union[List[str], Dict]]:
    """Get feature names and datatypes after transformation."""
    # extract numerical and categorical feature names in trained preprocessor
    numericals_processed = (
        pipe.named_steps["preprocessor"]
        .named_transformers_["num"]
        .named_steps[num_last_step]
        .get_feature_names_out()
    )
    rarecats_bucket_features_out = [
        c.split("__")[-1] for c in categorical_features
    ]
    categoricals_processed = (
        pipe.named_steps["preprocessor"]
        .named_transformers_["cat"]
        .named_steps["dummy"]
        .get_feature_names_out(rarecats_bucket_features_out)
        .tolist()
    )
    categoricals_processed = [
        c.replace(f"{cat_col}_", f"{cat_col}__")
        for c in categoricals_processed
        for cat_col in categorical_features
        if c.startswith(cat_col)
    ]

    # extract numerical and categorical feature names in selected features
    feats_selected = pipe.named_steps[pipe_last_step].get_feature_names_out(
        numericals_processed + categoricals_processed
    )
    cats_selected = [c for c in categoricals_processed if c in feats_selected]
    nums_selected = [c for c in numericals_processed if c in feats_selected]

    # get feature datatypes in selected features
    processed_dtypes = dict(
        zip(
            feats_selected,
            # [pd.Float32Dtype() for _ in nums_selected]
            # + [pd.Int8Dtype() for _ in cats_selected],
            [pd.Float64Dtype() for _ in nums_selected]
            + [pd.Int64Dtype() for _ in cats_selected],
        )
    )
    return [feats_selected, processed_dtypes]


def transform_data(
    X: pd.DataFrame, dtypes_dict: Dict, features: List[str], pipe: Pipeline
) -> pd.DataFrame:
    """Transform data and create DataFrame with transformed feature names."""
    X_trans = pipe.transform(X)
    feats_trans = dict(zip(list(X_trans), features))
    X_trans = X_trans.rename(columns=feats_trans).astype(dtypes_dict)
    return X_trans
