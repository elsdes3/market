#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities score predictions."""

# pylint: disable=invalid-name,dangerous-default-value,too-many-arguments
# pylint: disable=too-many-locals,unused-argument,redefined-outer-name

from typing import Dict, List, Union

import pandas as pd
import sklearn.metrics as skm


def pr_auc_score(y_true, y_score, sample_weight=None):
    """Calculate area under PR Curve."""
    precision, recall, _ = skm.precision_recall_curve(
        y_true, y_score, sample_weight=sample_weight
    )
    pr_auc = skm.auc(recall, precision)
    return pr_auc


def get_scorers(
    average: str = "macro", zero_division: str = "warn", sample_weight=None
) -> Dict:
    """Get dictionary of scorers."""
    scorers_dict = {
        "accuracy": skm.make_scorer(skm.accuracy_score),
        "balanced_accuracy": skm.make_scorer(skm.balanced_accuracy_score),
        "precision": skm.make_scorer(
            skm.precision_score,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
        ),
        "recall": skm.make_scorer(
            skm.recall_score,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
        ),
        "roc_auc": skm.make_scorer(
            skm.roc_auc_score,
            average=average,
            sample_weight=sample_weight,
        ),
        "f1": skm.make_scorer(
            skm.f1_score,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
        ),
        "fbeta05": skm.make_scorer(
            skm.fbeta_score,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
            beta=0.5,
        ),
        "fbeta2": skm.make_scorer(
            skm.fbeta_score,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
            beta=2,
        ),
        "pr_auc": skm.make_scorer(pr_auc_score, needs_proba=True),
        "avg_precision": skm.make_scorer(
            skm.average_precision_score,
            average=average,
            sample_weight=sample_weight,
        ),
    }
    return scorers_dict


def get_metrics(
    y_true: pd.Series,
    y_pred: pd.Series,
    y_pred_proba: pd.Series,
    average: str = "macro",
    zero_division: str = "warn",
    sample_weight=None,
) -> Dict:
    """Get dictionary of scorers."""
    metrics_dict = {
        "accuracy": skm.accuracy_score(y_true, y_pred),
        "balanced_accuracy": skm.balanced_accuracy_score(y_true, y_pred),
        "precision": skm.precision_score(
            y_true,
            y_pred,
            zero_division=zero_division,
            sample_weight=sample_weight,
        ),
        "recall": skm.recall_score(
            y_true,
            y_pred,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
        ),
        "roc_auc": skm.roc_auc_score(
            y_true,
            y_pred,
            average=average,
            sample_weight=sample_weight,
        ),
        "f1": skm.f1_score(
            y_true,
            y_pred,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
        ),
        "fbeta05": skm.fbeta_score(
            y_true,
            y_pred,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
            beta=0.5,
        ),
        "fbeta2": skm.fbeta_score(
            y_true,
            y_pred,
            average=average,
            zero_division=zero_division,
            sample_weight=sample_weight,
            beta=2,
        ),
        "pr_auc": pr_auc_score(
            y_true, y_pred_proba, sample_weight=sample_weight
        ),
        "avg_precision": skm.average_precision_score(
            y_true,
            y_pred,
            average=average,
            sample_weight=sample_weight,
        ),
    }
    return metrics_dict


def calculate_metrics(
    y_train: pd.Series,
    y_train_pred: pd.Series,
    y_train_pred_proba: pd.Series,
    y_test: Union[pd.Series, None] = None,
    y_test_pred: Union[pd.Series, None] = None,
    y_test_pred_proba: Union[pd.Series, None] = None,
    series_names: List[pd.Series] = ["train_val", "test"],
) -> pd.DataFrame:
    """Calculate metrics and summarize in a DataFrame."""
    if y_test is not None:
        y_trues = [y_train, y_test]
        y_preds = [y_train_pred, y_test_pred]
        y_pred_probas = [y_train_pred_proba, y_test_pred_proba]
    else:
        y_trues = [y_train]
        y_preds = [y_train_pred]
        y_pred_probas = [y_train_pred_proba]
    df_metrics = (
        pd.concat(
            [
                pd.DataFrame.from_dict(
                    get_metrics(
                        y_true, y_pred, y_pred_proba, "macro", "warn", None
                    ),
                    orient="index",
                )
                .transpose()
                .assign(split=s)
                for s, y_true, y_pred, y_pred_proba in zip(
                    series_names, y_trues, y_preds, y_pred_probas
                )
            ],
            axis=0,
            ignore_index=True,
        )
        .set_index("split")
        .transpose()
        .reset_index()
        .rename(columns={"index": "metric"})
    )
    return df_metrics
