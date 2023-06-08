#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to manage MLFlow models."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument
# pylint: disable=missing-class-docstring

from sklearn.base import BaseEstimator, TransformerMixin


class AboveAveragePagePromoEngager(BaseEstimator, TransformerMixin):
    """Get ratio to average page promotions."""

    def __init__(self, cols: list[str]):
        """."""
        self.cols = cols

        self.columns_trans = None

    def fit(self, X, y=None):
        """Train."""
        return self

    def transform(self, X):
        "Transform."
        for c in self.cols:
            f = f"above_avg_{c}"
            X[f] = 0 if X[c].mean() == 0 else X[c] / X[c].mean()
        self.columns_trans = X.columns.tolist()
        return X

    def get_feature_names_out(self):
        """Get transformed feature names."""
        return self.columns_trans
