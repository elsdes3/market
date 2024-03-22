#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to check data quality."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument
# pylint: disable=missing-class-docstring

import json
from datetime import datetime
from typing import Dict, List, Union

import evidently.tests as eaits
import pandas as pd
import pytz
from evidently.test_suite import TestSuite
from scipy import spatial, stats


def detect_features_drift(
    curr_data: pd.DataFrame,
    refer_data: pd.DataFrame,
    numericals: List[str],
    categoricals: List[str],
    kst_threshold: float = 0.05,
    kst_params: Dict[str, Union[str, int]] = dict(
        method="exact", N=20, alternative="two-sided"
    ),
    wsd_threshold: float = 0.5,
    jsd_threshold: float = 0.5,
) -> pd.DataFrame:
    """Perform checks for drift in features, using reference dataset."""
    len_smaller_dataset = min(len(refer_data), len(curr_data))
    categorical_stats_summary = []
    for c in categoricals:
        # get drift stats
        if len(curr_data) <= 1_000:
            csd = None
        else:
            jsd = spatial.distance.jensenshannon(
                curr_data[c]
                .astype("int64")  # int16
                .head(len_smaller_dataset)
                .to_numpy(),
                refer_data[c]
                .astype("int64")  # int16
                .head(len_smaller_dataset)
                .to_numpy(),
            )
        # get summary stats
        summary_stats = {
            "feature_type": "categorical",
            "feature": c,
            "nunique_ref": refer_data[c].nunique(),
            "nunique_curr": curr_data[c].nunique(),
            "metric_value": csd if len(curr_data) <= 1_000 else jsd,
            "metric_threshold": None
            if len(curr_data) <= 1_000
            else jsd_threshold,
        }
        df_cat_stats = pd.DataFrame.from_dict(
            summary_stats, orient="index"
        ).transpose()
        # check if drift is present
        if len(curr_data) <= 1_000:
            df_cat_stats = pd.DataFrame()
        else:
            df_cat_stats = df_cat_stats.assign(
                drift_detected=lambda df: df["metric_value"]
                > df["metric_threshold"]
            ).assign(test_type="Jensen-Shannon")
        categorical_stats_summary.append(df_cat_stats)

    numerical_stats_summary = []
    for c in numericals:
        # get descriptive stats
        feat_desc_stats = (
            refer_data[c]
            .describe()
            .rename("ref")
            .to_frame()
            .merge(
                curr_data[c].describe().rename("curr").to_frame(),
                left_index=True,
                right_index=True,
                how="left",
            )
            .assign(abs_diff=lambda df: df["ref"] - df["curr"])
            .assign(pct_diff=lambda df: 100 * (df["abs_diff"] / df["ref"]))
            .assign(feature=c)
        )
        # get drift stats
        refer_data_arr, curr_data_arr = [
            refer_data[c].to_numpy(),
            curr_data[c].to_numpy(),
        ]
        if len(curr_data) <= 1_000:
            kst = stats.kstest(refer_data_arr, curr_data_arr, **kst_params)
        else:
            wsd = stats.wasserstein_distance(refer_data_arr, curr_data_arr)
        # get summary stats
        summary_stats = {
            "feature_type": "numerical",
            "feature": c,
            "nunique_ref": refer_data[c].nunique(),
            "nunique_curr": curr_data[c].nunique(),
            "pct_diff_mean": feat_desc_stats["pct_diff"]["mean"],
            "pct_diff_std": feat_desc_stats["pct_diff"]["std"],
            "abs_diff_mean": feat_desc_stats["abs_diff"]["mean"],
            "abs_diff_std": feat_desc_stats["abs_diff"]["std"],
            "metric_value": kst.pvalue if len(curr_data) <= 1_000 else wsd,
            "metric_threshold": kst_threshold
            if len(curr_data) <= 1_000
            else wsd_threshold,
        }
        df_num_stats = pd.DataFrame.from_dict(
            summary_stats, orient="index"
        ).transpose()
        # check if drift is present
        if len(curr_data) <= 1_000:
            df_num_stats = (
                df_num_stats.assign(
                    reject_null=lambda df: df["metric_value"]
                    < df["metric_threshold"]
                )
                .assign(drift_detected=lambda df: df["reject_null"])
                .assign(test_type="Kolmogorov-Smirnov")
            )
            for k, v in kst_params.items():
                df_num_stats[k] = v
        else:
            df_num_stats = df_num_stats.assign(
                drift_detected=lambda df: df["metric_value"]
                > df["metric_threshold"]
            ).assign(test_type="Wasserstein")
        numerical_stats_summary.append(df_num_stats)

    df_num_stats = pd.concat(
        numerical_stats_summary or [pd.DataFrame()], ignore_index=True
    )
    df_cat_stats = pd.concat(
        categorical_stats_summary or [pd.DataFrame()], ignore_index=True
    )
    return [df_num_stats, df_cat_stats]


def check_data_stability(
    curr_data: pd.DataFrame,
    refer_data: pd.DataFrame,
    numericals: List[str],
    categoricals: List[str],
) -> pd.DataFrame:
    """Check subset of features for data stability using reference dataset."""
    ts_cols_eai = categoricals + numericals
    start_time = datetime.now(pytz.timezone("US/Eastern"))
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"Test suite start time = {start_time_str[:-3]}...", end="")
    tests = TestSuite(
        tests=[
            eaits.TestNumberOfColumnsWithMissingValues(),
            eaits.TestNumberOfRowsWithMissingValues(),
            eaits.TestNumberOfConstantColumns(),
            eaits.TestNumberOfDuplicatedRows(),
            eaits.TestNumberOfDuplicatedColumns(),
            # eaits.TestColumnsType(),
            eaits.TestNumberOfEmptyColumns(),
            eaits.TestNumberOfEmptyRows(),
            eaits.TestNumberOfRowsWithMissingValues(),
            eaits.TestNumberOfColumns(),
        ]
    )
    tests.run(
        reference_data=refer_data[ts_cols_eai],
        current_data=curr_data[ts_cols_eai],
    )
    end_time = datetime.now(pytz.timezone("US/Eastern"))
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    duration = end_time - start_time
    duration = duration.seconds + (duration.microseconds / 1_000_000)
    print(f"done at {end_time_str[:-3]} ({duration:.3f} seconds).")
    df_stability = (
        pd.DataFrame.from_dict(tests.as_dict()["summary"], orient="index")
        .transpose()
        .assign(len_curr_data=len(curr_data))
        .assign(len_ref_data=len(refer_data))
        .assign(features_checked=json.dumps(ts_cols_eai))
        .assign(num_features_checked=len(ts_cols_eai))
    )
    df_stability = df_stability.join(
        pd.json_normalize(df_stability["by_status"])
    ).drop(columns=["by_status"])
    return df_stability
