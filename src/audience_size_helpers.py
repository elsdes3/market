#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to estimate audience sizes."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments


import os
from typing import Dict, List, Tuple, Union

import pandas as pd

from stats_helpers import calc_chisquared_sample_size


def calc_sample_size_multiple_audience_groups(
    group_number: int,
    group_size: int,
    min_proba: float,
    conv_rate_pct: float,
    ctr_pct: float,
    revenue: float,
    bounce_rate: float,
    uplift: int,
    power: int,
    ci_level: int,
) -> dict:
    """Get sample size to target visitors in multiple propensity groups."""
    sample_size_dict = {
        "group_number": group_number,
        "group_size": group_size,
        "group_min_propensity": min_proba,
        "group_conv_rate": conv_rate_pct,
        "ctr": ctr_pct,
        "revenue": revenue,
        "bounce_rate": bounce_rate,
        "uplift": uplift,
        "power": power,
        "ci_level": ci_level,
        "required_sample_size": calc_chisquared_sample_size(
            conv_rate_pct, uplift, power, ci_level
        ),
    }
    return sample_size_dict


def calc_sample_size_single_audience_group(
    group_number: int,
    group_size: int,
    group_size_prop: float,
    min_proba: float,
    conv_rate_pct: float,
    ctr_pct: float,
    revenue: float,
    bounce_rate: float,
    uplift_pct: int,
    power_pct: int,
    confidence_level_pct: int,
) -> dict:
    """Get sample size to target visitors in top propensity group."""
    sample_size_dict = {
        "group_number": group_number,
        "group_size": group_size,
        "group_size_proportion": group_size_prop,
        "group_min_propensity": min_proba,
        "group_conv_rate": conv_rate_pct,
        "ctr": ctr_pct,
        "revenue": revenue,
        "bounce_rate": bounce_rate,
        "uplift": uplift_pct,
        "power": power_pct,
        "ci_level": confidence_level_pct,
        "required_sample_size": calc_chisquared_sample_size(
            conv_rate_pct, uplift_pct, power_pct, confidence_level_pct
        ),
    }
    return sample_size_dict


def sort_scores(df: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    """Sort predicted propensity (probability) scores."""
    df = df.sort_values(by=["score"], ascending=ascending)
    return df


def get_group_size(df: pd.DataFrame, num_groups: int) -> int:
    """Calculate size of audience group (bin)."""
    num_observations = len(df)
    group_size = int(num_observations / num_groups)
    return group_size


def get_audience_groups_by_propensity(
    df: pd.DataFrame, num_groups: int
) -> pd.DataFrame:
    """Divide samples into groups (quantiles) from predicted propensity."""
    df = df.assign(row_number=lambda df: range(len(df))).assign(
        group_number=lambda df: pd.qcut(
            x=df["row_number"], q=num_groups, labels=False
        )
    )
    return df


def get_kpi_per_audience_group(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate KPI for each audience group."""
    col_renamer_dict = {"fullvisitorid": "conversions", "score": "min_score"}
    kpi, tot_visitors = ["conversions", "total_visitors"]
    # get stats for group
    df_group_stats = (
        df.groupby("group_number", as_index=False)
        .agg(
            {
                "fullvisitorid": "count",
                # get first-visit bounces per group
                "bounces": "sum",
                # get first-visit revenue per group
                "revenue": "sum",
                # get first-visit clicks per group
                "product_clicks": "sum",
                # get first-visit views per group
                "product_views": "sum",
            }
        )
        .rename(
            columns={
                "fullvisitorid": tot_visitors,
                "product_clicks": "clicks",
                "product_views": "views",
            }
        )
        .astype({tot_visitors: pd.Float64Dtype()})
        # get first-visit CTR per group
        .assign(ctr=lambda df: 100 * df["clicks"] / df["views"])
        # get first-visit bounce rate per group
        .assign(bounce_rate=lambda df: 100 * df["bounces"] / df[tot_visitors])
    )
    # get stats for conversions within group
    df_group_stats_convs = (
        df.query("label == 1")
        .groupby("group_number", as_index=False)
        .agg({"fullvisitorid": "count", "score": "min"})
        .rename(columns=col_renamer_dict)
    )
    df = (
        df_group_stats_convs.merge(
            df_group_stats, on="group_number", how="left"
        )
        # get conversion rate per group
        .assign(conversion_rate=lambda df: 100 * df[kpi] / df[tot_visitors])
    )
    return df


def calculate_multi_group_sample_sizes(
    df_kpis: pd.DataFrame,
    uplift_range: Tuple[int],
    power_range: Tuple[int],
    ci_level_range: Tuple[int],
) -> pd.DataFrame:
    """Calculate sample size for low, mid & high-propensity audience group."""
    df = pd.DataFrame.from_records(
        [
            calc_sample_size_multiple_audience_groups(
                row["group_number"],
                row["total_visitors"],
                row["min_score"],
                row["conversion_rate"],
                row["ctr"],
                row["revenue"],
                row["bounce_rate"],
                uplift,
                power,
                ci_level,
            )
            for _, row in df_kpis.iterrows()
            for uplift in uplift_range
            for power in power_range
            for ci_level in ci_level_range
        ]
    )
    return df


def calculate_single_group_sample_sizes(
    df: pd.DataFrame,
    num_groups: int,
    audience_group_size: int,
    uplift_range: Tuple[int],
    power_range: Tuple[int],
    confidence_level_range: Tuple[int],
) -> pd.DataFrame:
    """Calculate sample sizes for high-propensity audience group."""
    top_group_sample_size_records = []
    for audience_group_number in range(1, (num_groups + 1)):
        # get bin (or group) size to capture upper N% of samples (visitors)
        current_bin_size = audience_group_size * audience_group_number

        # get observations that fall into bin with upper N% of samples
        audience_group_visitors = df.head(current_bin_size)

        # calculate conversion rate (KPI) for bin with upper N% of samples
        clicks, views, bnc = ["product_clicks", "product_views", "bounces"]
        # get conversions within group
        df_kpi = audience_group_visitors.query("label == 1")
        # get conversion rate per group
        binned_conversion_rate = 100 * len(df_kpi) / current_bin_size
        # get first-visit CTR per group
        group_clicks = audience_group_visitors[clicks].sum()
        group_views = audience_group_visitors[views].sum()
        binned_ctr = 100 * group_clicks / group_views
        # get first-visit bounce rate per group
        group_bounces = audience_group_visitors[bnc].sum()
        binned_bounce_rate = 100 * (group_bounces / current_bin_size)
        # get first-visit revenue per group
        binned_revenue = audience_group_visitors["revenue"].sum()

        # get sample sizes
        for uplift in uplift_range:
            for power in power_range:
                for ci_level in confidence_level_range:
                    sample_size_dict = calc_sample_size_single_audience_group(
                        audience_group_number,
                        current_bin_size,
                        100 * current_bin_size / len(df),
                        audience_group_visitors["score"].min(),
                        binned_conversion_rate,
                        binned_ctr,
                        binned_revenue,
                        binned_bounce_rate,
                        uplift,
                        power,
                        ci_level,
                    )
                    top_group_sample_size_records.append(sample_size_dict)
    df_sample_sizes = pd.DataFrame.from_records(top_group_sample_size_records)
    return df_sample_sizes


def invert_group_numbers(df: pd.DataFrame, num_groups: int) -> pd.DataFrame:
    """Invert group numbers to convention for ordering quantiles, & sort."""
    df = (
        df
        # we want lowest bin (or group) number associated with highest score
        # if df_prediction.sort_values(by=['score']) is performed in ascending
        # order then lowest group number is associated with lowest score and
        # group numbers need to be inverted, else no changes are needed
        .assign(group_number=lambda df: num_groups - df["group_number"] - 1)
        # order by bin number so bins are displayed in meaningful order
        .sort_values(["group_number"], ignore_index=True)
    )
    return df


def subtract_one_from_group_numbers(
    df: pd.DataFrame, group_num_col: str = "group_number"
) -> pd.DataFrame:
    """Subtract one from cumulative group (bin) numbers."""
    df[group_num_col] = df[group_num_col] - 1
    return df


def map_audience_group_number_to_name(
    df: pd.DataFrame,
    group_mapper_dict: Dict,
    group_num_column: str = "group_number",
) -> pd.DataFrame:
    """Map group numbers to names (0: High propensity, 1: Medium, 2: Low)."""
    df = df.assign(
        maudience=lambda df: df[group_num_column].map(group_mapper_dict)
    )
    return df


def set_datatypes(df: pd.DataFrame, dtypes_dict: Dict) -> pd.DataFrame:
    """Set column datatypes for DataFrame."""
    cols_data = [c for c in list(dtypes_dict) if c in list(df)]
    if cols_data:
        df = df.astype(dtypes_dict)
        print("Set all specified datatypes.")
    else:
        print("Mismatch between dtypes dict & columns. Did nothing.")
    return df


def move_cols_to_front(df: pd.DataFrame, cols_to_move: list) -> pd.DataFrame:
    """Move list of columns to front of DataFrame."""
    new_col_order = cols_to_move + [
        c for c in list(df) if c not in cols_to_move
    ]
    df = df.filter(new_col_order)
    return df


def combine_and_export_sample_size_estimates(
    df_multi_group: pd.DataFrame,
    df_single_group: pd.DataFrame,
    df_best_run: pd.DataFrame,
    aud_size_file_dir: str,
) -> List[Union[pd.DataFrame, str]]:
    """Export both experiment design sample size estimates to disk."""
    best_run_id = df_best_run.squeeze()["run_id"]
    df = pd.concat(
        [
            df_multi_group.assign(audience_strategy=1),
            df_single_group.assign(audience_strategy=2),
        ],
        ignore_index=True,
    )
    aud_sizes_fpath = os.path.join(
        aud_size_file_dir,
        f"audience_sample_sizes__run_{best_run_id}.parquet.gzip",
    )
    df.to_parquet(
        aud_sizes_fpath, index=False, engine="pyarrow", compression="gzip"
    )
    print(
        f"Exported {len(df):,} rows and {df.shape[1]:,} columns of sample "
        "size estimates, using both (a) all visitors and (b) only high-"
        f"propensity visitors, to {os.path.basename(aud_sizes_fpath)}"
    )
    return [df, aud_sizes_fpath]
