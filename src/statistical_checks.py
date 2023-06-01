#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to manage post-campaign statistical analysis."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument


from typing import List, Tuple

import numpy as np
import pandas as pd
from statsmodels.stats import proportion

import model_helpers as modh


def get_inference_data_with_cohorts(
    df_best_model_runs: pd.DataFrame, fname_prefix: str
) -> pd.DataFrame:
    """Load inference data with audience cohorts."""
    df = modh.get_data_for_run_id(df_best_model_runs, fname_prefix)
    return df


def get_outcome_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Load outcome for first-time visitors during inference period."""
    rng = np.random.default_rng(88)
    y = pd.Series(
        rng.beta(a=0.32, b=2.25, size=len(df)) >= 0.5, dtype=pd.BooleanDtype()
    )
    df = df.assign(label=y)
    return df


def get_cohorts(df: pd.DataFrame, cohort_col: str) -> pd.DataFrame:
    """Extract observations that were assigned to a cohort."""
    df = df.query(f"~{cohort_col}.isna()")
    return df


def get_overall_and_converted_cohort_sizes(
    data: pd.DataFrame, verbose: bool = False
) -> List[Tuple[int]]:
    """Get size of overall cohort and conversions in cohort."""
    df_control_group = data.query("(cohort == 'Control')")
    df_control_group_conversions = df_control_group.query("label == True")
    df_test_group = data.query("cohort == 'Test'")
    df_test_group_conversions = df_test_group.query("label == True")
    if verbose:
        print(
            f"Cohort Sizes:\nControl: Overall={len(df_control_group):,}, "
            f"Conversions={len(df_control_group_conversions):,}\n"
            f"Test: Overall={len(df_test_group):,}, "
            f"Conversions={len(df_test_group_conversions):,}"
        )
    return [
        (len(df_test_group), len(df_control_group)),
        (len(df_test_group_conversions), len(df_control_group_conversions)),
    ]


def check_significance_using_chisq(
    overall_sizes: Tuple[int],
    conversions_sizes: Tuple[int],
    ci_levels: np.ndarray = [0.95],
) -> float:
    """Check if diff. in conversions is stat. significant between cohorts."""
    _, p_value, _ = proportion.proportions_chisquare(
        count=conversions_sizes, nobs=overall_sizes
    )
    sig_checks = []
    for ci_level in ci_levels:
        if p_value < (1 - ci_level):
            msg = "statistically significant"
        else:
            msg = "not statistically significant"
        summary_dict = {
            "p_value": p_value,
            "ci_level": int(100 * ci_level),
            "check": msg,
        }
        sig_checks.append(summary_dict)
    df_sig_checks = (
        pd.DataFrame.from_records(sig_checks)
        .groupby("check", as_index=False)
        .agg({"p_value": "first", "ci_level": "max"})
        .assign(control_overall=overall_sizes[1])
        .assign(test_overall=overall_sizes[0])
        .assign(control_conversions=conversions_sizes[1])
        .assign(test_conversions=conversions_sizes[0])
    )
    return df_sig_checks
