#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to manage audience cohorts."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument


from typing import Dict

import numpy as np
import pandas as pd

from model_helpers import get_data_for_run_id


def combine_infer_data(
    X: pd.DataFrame, y_pred: pd.Series, y_pred_proba: pd.Series
) -> pd.DataFrame:
    """Combine inference features and predictions."""
    df = X.assign(score=y_pred_proba).assign(
        predicted_score_label=lambda df: y_pred
    )
    return df


def rename_columns(df: pd.DataFrame, renamer_dict: dict) -> pd.DataFrame:
    """Rename DataFrame columns using dictionary."""
    df = df.rename(columns=renamer_dict)
    return df


def load_file_from_mlflow_artifact(
    df_models: pd.DataFrame,
    artifact_fname_prefix: str,
) -> pd.DataFrame:
    """Load file stored in MLFlow artifact into DataFrame."""
    df = get_data_for_run_id(df_models, artifact_fname_prefix)
    return df


def get_sample_sizes_by_strategy(
    df: pd.DataFrame, audience_strategy: int
) -> pd.DataFrame:
    """Filter recommended sample sizes by experiment method."""
    df = df.query(f"audience_strategy == {audience_strategy}")
    return df


def get_suitable_sample_sizes(
    df: pd.DataFrame, bin_size_infer_control: int
) -> pd.DataFrame:
    """Filter required sample sizes to get those supported by size of data."""
    df = df.query(f"required_sample_size <= {bin_size_infer_control}")
    return df


def get_sample_sizes_with_all_audience_groups(
    df: pd.DataFrame, num_groups: int
) -> pd.DataFrame:
    """Get sample sizes that support all required audience groups (bins)."""
    df = (
        df.assign(
            num_groups=lambda df: df.groupby(
                ["uplift", "power", "ci_level"],
                as_index=False,
                sort=False,
            )["maudience"].transform("count")
        )
        .query(f"num_groups == {num_groups}")
        .drop(columns=["num_groups"])
    )
    return df


def get_required_inputs(df: pd.DataFrame, query_inputs: str) -> pd.DataFrame:
    """Get required sample sizes for desired inputs."""
    df = df.query(query_inputs)
    return df


def create_cohorts(
    df_group_sizes: pd.DataFrame,
    df: pd.DataFrame,
    mapper_dict_audience: Dict[int, str],
    audience_strategy: int,
) -> pd.DataFrame:
    """Create audience cohorts."""
    if df_group_sizes.empty:
        print("Found no suitable sample sizes, so did not generate cohorts.")
        data_cols = [c for c in list(df) if c not in ["row_number"]]
        new_cols = ["cohort", "audience_strategy"]
        df_infer_audience_grps = pd.DataFrame(columns=data_cols + new_cols)
    else:
        groups = []
        cohort_sizes = df_group_sizes["required_sample_size"].tolist()
        for k, grp_size in enumerate(cohort_sizes):
            df_audience = df.query(f"maudience == {k}")
            audience_array = df_audience["fullvisitorid"].to_numpy()

            # 0. scale required sample size based on ratio of group sizes in
            # unseen to base datasets
            base_group_size = df_group_sizes.query(f"group_number == {k}")[
                "group_size"
            ].iloc[0]
            infer_group_size = len(df_audience)
            grp_size = int(grp_size * infer_group_size / base_group_size)

            # 1. get control group (visitors)
            rng = np.random.default_rng(88)
            control_grp = rng.choice(
                audience_array, grp_size, replace=False
            ).tolist()

            # 2. get all other visitors
            other_grp = list(set(audience_array) - set(control_grp))

            # 3. get test group from a random sample of the other visitors
            rng = np.random.default_rng(88)
            test_grp = rng.choice(other_grp, grp_size, replace=False).tolist()

            # 4. get combined control and test cohorts of visitors
            combined_cohort = control_grp + test_grp
            # get all excluded visitors (not part of test or control cohort)
            excluded_grp = list(set(audience_array) - set(combined_cohort))

            print(
                f"audience={k}: {mapper_dict_audience[k]}, "
                f"size={len(audience_array):,}, ",
                f"excluded={len(excluded_grp):,}, "
                f"wanted={grp_size:,}, "
                f"control={len(control_grp):,}, "
                f"test={len(test_grp):,}",
            )

            # 5. get extract attributes for each cohort per audience group
            df_test = (
                df_audience.drop(columns=["row_number"])
                .query("fullvisitorid.isin(@test_grp)")
                .assign(maudience=k)
                .assign(cohort="Test")
            )
            df_control = (
                df_audience.drop(columns=["row_number"])
                .query("fullvisitorid.isin(@control_grp)")
                .assign(maudience=k)
                .assign(cohort="Control")
            )
            df_excluded = (
                df_audience.drop(columns=["row_number"])
                .query("fullvisitorid.isin(@excluded_grp)")
                .assign(maudience=k)
                .assign(cohort=None)
            )
            df_coh = pd.concat(
                [df_control, df_test, df_excluded], ignore_index=True
            )
            groups.append(df_coh)
        df_infer_audience_grps = (
            pd.concat(groups, ignore_index=True)
            .assign(
                maudience=lambda df: df["maudience"].map(mapper_dict_audience)
            )
            .assign(audience_strategy=audience_strategy)
        )
        print("Found suitable sample sizes and generated cohorts.")
    return df_infer_audience_grps


def get_cohort_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Get descriptive statistics for audience cohorts."""
    df_aud_stats = (
        df.astype({"score": pd.Float64Dtype()})
        .groupby(["maudience", "cohort"], dropna=False, as_index=False)
        .agg({"score": ["count", "min", "mean", "median", "max"]})
    )
    df_aud_stats.columns = [
        "_".join(c).rstrip("_") for c in df_aud_stats.columns.to_flat_index()
    ]
    dtypes_dict = {
        # f"score_{stat}": pd.Float32Dtype()
        f"score_{stat}": pd.Float64Dtype()
        for stat in ["min", "mean", "median", "max"]
    }
    dtypes_dict.update({"score_count": pd.Int64Dtype()})
    df_aud_stats = df_aud_stats.astype(dtypes_dict).sort_values(
        by=["maudience"]
    )
    return df_aud_stats
