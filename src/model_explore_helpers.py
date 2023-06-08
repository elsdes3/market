#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities explore trained ML models."""

# pylint: disable=invalid-name,dangerous-default-value,too-many-arguments
# pylint: disable=too-many-locals,unused-argument,redefined-outer-name


from typing import List, Union

import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline

import preprocess_helpers as prh


def get_preprocessor_pipeline(
    pipe: Pipeline, resampling_approach: str
) -> List[Pipeline]:
    """Get preprocessor and/or resampling pipelines."""
    if resampling_approach == "us":
        pipe_resample_trans = clone(pipe)
        pipe_resample_trans.steps.pop(-1)
        return [pipe_resample_trans]
    else:
        pipe_resample = pipe.named_steps["resampler"]
        pipe_trans = clone(pipe)
        pipe_trans.steps.pop(-1)
        pipe_trans.steps.pop(-1)
        return [pipe_trans, pipe_resample]


def get_preprocessed_resampled_data(
    resampling_approach: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    categorical_features: List[str],
    pipe_trans: Union[Pipeline, None] = None,
    pipe_resample_trans: Union[Pipeline, None] = None,
    pipe_resample: Union[Pipeline, None] = None,
) -> List[Union[pd.DataFrame, pd.Series]]:
    """Get data after preprocessing and resampling."""
    if resampling_approach == "os":
        # train pre-processor using training data
        _ = pipe_trans.fit(X_train, y_train)

        # pre-process training and test data
        feats_trans, trans_dtypes = prh.get_transformed_features(
            pipe_trans, "aboveavg", "select", categorical_features
        )
        X_train_trans = prh.transform_data(
            X_train, trans_dtypes, feats_trans, pipe_trans
        )
        X_test_trans = prh.transform_data(
            X_test, trans_dtypes, feats_trans, pipe_trans
        )

        # over-sample pre-processed training data
        X_train_trans_rs, y_train_trans_rs = pipe_resample.fit_resample(
            X_train_trans, y_train
        )
        Xy_trans_resample = [
            X_train_trans,
            X_test_trans,
            X_train_trans_rs,
            y_train_trans_rs,
        ]
        return Xy_trans_resample
    else:
        # train pre-processor using under-sampled training data
        _ = pipe_resample_trans.fit(X_train, y_train)

        # pre-process under-sampled training and raw test data
        feats_trans, trans_dtypes = prh.get_transformed_features(
            pipe_resample_trans, "aboveavg", "select", categorical_features
        )
        X_train_trans = prh.transform_data(
            X_train, trans_dtypes, feats_trans, pipe_resample_trans
        )
        X_test_trans = prh.transform_data(
            X_test, trans_dtypes, feats_trans, pipe_resample_trans
        )
        return [X_train_trans, X_test_trans]
