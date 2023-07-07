#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to manage scikit-learn model objects."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments
# pylint: disable=too-many-instance-attributes


import numpy as np
import pandas as pd
import sklearn.metrics as skm
import sklearn.utils.validation as skc
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.multiclass import unique_labels


class BetaDistClassifier(BaseEstimator, ClassifierMixin):
    """Make predictions based on a continuous beta probability distribution."""

    def __init__(
        self,
        threshold: float = 0.5,
        a: float = 2.31,
        b: float = 0.627,
        random_state=None,
    ):
        """
        Initializes BetaDistClassifier.

        Args:
            a: alpha parameter of beta distribution
            b: beta parameter of beta distribution
            threshold: classification discrimination threshold
            random_state: Controls randomness when sampling from beta distribn
        """
        self.random_state = random_state
        self.threshold = threshold
        self.a = a
        self.b = b

    def fit(self, X, y):
        """Fit estimator."""
        # self.n_features_in_ = X.shape[1]
        # self.feature_names_in_ = X.columns.to_numpy()

        # Check that X and y have correct shape
        X, y = skc.check_X_y(X, y)

        # Store the classes seen during fit
        self.classes_ = unique_labels(y)

        self.X_ = X
        self.y_ = y
        self.random_state_ = skc.check_random_state(self.random_state)

        # set attribute for scikit-learn
        self.fitted_ = True
        return self

    def predict_proba(self, X):
        """Make probabilistic predictions for X."""
        # Check if fit has been called
        skc.check_is_fitted(self)

        # Input validation
        X = skc.check_array(X)

        # randomly sample from beta distribution with specified params a and b
        n_samples = X.shape[0]
        y_proba = self.random_state_.beta(a=self.a, b=self.b, size=n_samples)

        # return 2D array for predictions per class (1st column is majority
        # class and second column is minority class)
        y_proba = np.stack([1 - y_proba, y_proba]).T
        return y_proba

    def predict(self, X):
        """Predict class for X."""
        # Check if fit has been called
        skc.check_is_fitted(self)

        # Input validation
        X = skc.check_array(X)

        # get class labels from predicted probabilities
        y = (self.predict_proba(X) > self.threshold).astype(int)[:, 1]
        return y

    def get_params(self, deep=True):
        """Get parameters for this estimator."""
        return {
            "a": self.a,
            "b": self.b,
            "threshold": self.threshold,
            "random_state": self.random_state,
        }

    def set_params(self, **parameters):
        """Set the parameters of this estimator."""
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self


def get_threshold_stats(df: pd.DataFrame):
    """Get descriptive stats and default score from varying threshold."""
    df_default_threshold = (
        df.query("t == 0.5")
        .transpose()
        .squeeze()
        .rename("t=0.5")
        .reset_index()
        .rename(columns={"index": "metric"})
    )
    df_threshold_stats = (
        df.drop(columns=["t"])
        .describe()
        .transpose()
        .reset_index()
        .drop(columns=["count"])
        .rename(columns={"index": "metric"})
    )
    df_combo_stats = df_default_threshold.merge(
        df_threshold_stats, on="metric", how="inner"
    )
    return df_combo_stats


def get_threshold_tuning_scores(
    y_true: pd.Series,
    y_pred_proba: pd.Series,
    thresholds: np.ndarray = np.arange(0, 1, 0.01),
    average: str = "macro",
    zero_division: str = "warn",
    sample_weight=None,
) -> pd.DataFrame:
    """Get scores from varying discrimination threshold."""
    scores_thresholds = [
        {
            "t": t,
            "accuracy": skm.accuracy_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
            ),
            "balanced_accuracy": skm.balanced_accuracy_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
            ),
            "precision": skm.precision_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
                zero_division=zero_division,
                sample_weight=sample_weight,
            ),
            "recall": skm.recall_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
                average=average,
                zero_division=zero_division,
                sample_weight=sample_weight,
            ),
            "roc_auc": skm.roc_auc_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
                average=average,
                sample_weight=sample_weight,
            ),
            "f1": skm.f1_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
                average=average,
                zero_division=zero_division,
                sample_weight=sample_weight,
            ),
            "fbeta05": skm.fbeta_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
                average=average,
                zero_division=zero_division,
                sample_weight=sample_weight,
                beta=0.5,
            ),
            "fbeta2": skm.fbeta_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
                average=average,
                zero_division=zero_division,
                sample_weight=sample_weight,
                beta=2,
            ),
            "avg_precision": skm.average_precision_score(
                y_true,
                (y_pred_proba.squeeze() >= t).astype(pd.Int8Dtype()),
                average=average,
                sample_weight=sample_weight,
            ),
        }
        for t in thresholds
    ]
    df_thresholds = pd.DataFrame.from_records(scores_thresholds)
    return df_thresholds
