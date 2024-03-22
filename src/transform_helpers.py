#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to transform raw data."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments

import os
from typing import Dict, List, Union

import pandas as pd

import categorical_helpers as ch
import sql_helpers as sq


def set_datatypes(df: pd.DataFrame, dtypes: Dict) -> pd.DataFrame:
    """Set DataFrame datatypes using dictionary."""
    df = df.astype(dtypes)
    return df


def drop_duplicates(df: pd.DataFrame, subset: List[str]) -> pd.DataFrame:
    """Drop duplicates."""
    df = df.drop_duplicates(subset=subset, keep="first")
    duplicates_str = ", ".join(subset)
    print(
        f"Got {len(df):,} rows and {df.shape[1]:,} columns "
        f"after dropping duplicates by {duplicates_str}"
    )
    return df


def map_columns(df: pd.DataFrame, mapper_dict: Dict) -> pd.DataFrame:
    """Map values in DataFrame column using dictionary."""
    for k, v in mapper_dict.items():
        df[k] = df[k].map(v)
    return df


def shuffle_data(df: pd.DataFrame) -> pd.DataFrame:
    """Shuffle data."""
    df = df.sample(frac=1.0, random_state=88)
    return df


def extract_data(query: str, gcp_auth_dict: Dict) -> pd.DataFrame:
    """Retrieve data from Google BigQuery dataset."""
    df = sq.run_sql_query(query, **gcp_auth_dict, show_df=False)
    return df


def transform_data(
    df: pd.DataFrame,
    datatypes_dict: Dict,
    duplicate_cols: List[str],
    column_mapper_dict: Dict[int, str],
    categoricals: List[str] = [],
) -> List[Union[pd.DataFrame, List[Dict]]]:
    """Transform features in data."""
    df, cat_mapper_dicts = (
        df.pipe(set_datatypes, datatypes_dict)
        .pipe(drop_duplicates, duplicate_cols)
        .pipe(map_columns, column_mapper_dict)
        .pipe(ch.cast_categoricals_as_ints, categoricals)
    )
    print(f"Transformed data has {len(df):,} rows & {df.shape[1]:,} columns")
    return [df, cat_mapper_dicts]


def create_combined_validation_data(
    df_train: pd.DataFrame, df_val: pd.DataFrame, datatypes_dict: Dict
) -> List[pd.DataFrame]:
    """Extract training & combined training+validation data for validation."""
    df_train_val = pd.concat(
        [
            df_train.assign(split="train").pipe(shuffle_data),
            df_val.assign(split="val"),
        ]
    ).pipe(set_datatypes, datatypes_dict)
    df_train = df_train_val.query("split == 'train'")
    df_train, df_train_val = [
        df.drop(columns=["split"]) for df in [df_train, df_train_val]
    ]
    return [df_train, df_train_val]


def load_data(
    df: pd.DataFrame, processed_data_dir: str, split_type: str = "train"
) -> None:
    """Save data to file on local disk."""
    fpath = os.path.join(
        processed_data_dir, f"{split_type}_processed.parquet.gzip"
    )
    df.to_parquet(fpath, index=False, compression="gzip", engine="pyarrow")
    print(f"Exported data to {fpath}")


def get_conv_rate(
    df: pd.DataFrame, label_col: str = "predicted_score_label"
) -> float:
    """Calculate conversion rate."""
    conv_rate = 100 * df[label_col].sum() / len(df)
    return conv_rate


def perform_custom_aggregation(
    df: pd.DataFrame,
    groupby_cols: List[str],
    agg_dict: Dict[str, Union[List[str], str]],
    audience_strategy: int,
    column_renamer: Dict[str, str],
    dtypes_out: Dict,
    visitor_type_mapper: Dict[str, str] = dict(),
    visitor_type_col: str = "maudience",
    df_months_ordered: pd.DataFrame = pd.DataFrame(),
    zero_replacement_dict: Dict[str, Dict[int, None]] = {},
    cols_to_drop: List[str] = [],
    mom_stats: List[str] = [],
) -> pd.DataFrame:
    """."""
    # perform aggregations
    groupby_kwargs = dict(by=groupby_cols, as_index=False, sort=False)
    df_agg = df.groupby(**groupby_kwargs).agg(agg_dict)
    df_agg.columns = [
        "_".join(a).rstrip("_") for a in df_agg.columns.to_flat_index()
    ]
    df_agg = df_agg.assign(audience_strategy=audience_strategy).rename(
        columns=column_renamer
    )

    # (optional) sort by month, where month does not start at January
    if not df_months_ordered.empty:
        df_agg = df_months_ordered.merge(df_agg, on="month")
    else:
        df_agg = df_agg.assign(
            month=lambda df: pd.to_datetime(df["date"]).dt.month_name()
        )

    # add metadata
    clicks, views, vis = ["product_clicks", "product_views", "visitors"]
    df_agg = (
        df_agg
        # add rates
        .assign(bounce_rate=lambda df: 100 * df["bounces"] / df[vis])
        .assign(time_on_site=lambda df: df["time_on_site"] / 60)
        .assign(product_clicks_rate=lambda df: 100 * df[clicks] / df[views])
        .assign(add_to_cart_rate=lambda df: 100 * df["add_to_cart"] / df[vis])
    )
    # add indicator of the type of visitor
    # - return purchasers during ML development & all visitors in inference
    if visitor_type_mapper:
        df_agg = df_agg.assign(
            visitor_type=lambda df: df[visitor_type_col].map(
                visitor_type_mapper
            )
        )
    if (
        "conversion_rate" in list(dtypes_out)
        and "made_purchase_on_future_visit_sum" in list(column_renamer)
        and "made_purchase_on_future_visit" in list(agg_dict)
    ):
        df_agg = df_agg.assign(
            conversion_rate=lambda df: 100 * df["return_purchasers"] / df[vis]
        )

    # (optional) replace zeros with NaNs for inference data
    if zero_replacement_dict:
        df_agg = df_agg.replace(zero_replacement_dict)

    # (optional) drop unwanted columns and rename columns
    if cols_to_drop:
        df_agg = df_agg.drop(columns=cols_to_drop)

    # add month-over-month stats
    if mom_stats:
        for c in mom_stats:
            df_agg[f"{c}_pct_change"] = 100 * df_agg[c].pct_change()

    # set datatypes
    df_agg = df_agg.astype(dtypes_out)

    # move month column to front
    col = df_agg.pop("month")
    df_agg.insert(0, col.name, col)
    return df_agg


def group_infrequent_categories(s: pd.Series, f: str) -> pd.Series:
    """Group infrequent categories in a categorical into a single category."""
    freq_cats = (
        s.astype(pd.StringDtype())
        .value_counts(normalize=True)
        .reset_index()
        .assign(proportion=lambda df: df["proportion"] * 100)
        .query("proportion > 10")[f]
        .tolist()
    )
    all_freq_cats = s.astype(pd.StringDtype()).unique().tolist()
    infreq_cats = {f: "other" for f in set(all_freq_cats) - set(freq_cats)}
    mapper_freq_cats = {f: f for f in freq_cats}
    mapper_freq_cats.update(infreq_cats)
    s = s.astype(pd.StringDtype()).map(mapper_freq_cats)
    return s


def agg_kpis(df: pd.DataFrame, f: str) -> pd.DataFrame:
    """Aggregate KPIs by a single categorical feature."""
    pc, pv, vis, cr = [
        "product_clicks",
        "product_views",
        "visitors",
        "conversion_rate",
    ]
    df_agg = (
        df.astype(
            {
                f: pd.StringDtype(),
                "revenue": pd.Float64Dtype(),
                "made_purchase_on_future_visit": pd.Int64Dtype(),
                "product_clicks": pd.Int64Dtype(),  # Int32Dtype
                "product_views": pd.Int64Dtype(),  # Int32Dtype
            }
        )
        .groupby(f)
        .agg(
            {
                "revenue": "sum",
                "made_purchase_on_future_visit": "sum",
                "product_views": "sum",
                "product_clicks": "sum",
                "fullvisitorid": "count",
            }
        )
        .reset_index()
        .rename(
            columns={
                "fullvisitorid": "visitors",
                "made_purchase_on_future_visit": "conversions",
            }
        )
        .astype(
            {
                "conversions": pd.Int64Dtype(),  # Int32Dtype
                "visitors": pd.Int64Dtype(),  # Int32Dtype
                "revenue": pd.Float64Dtype(),  # Float32Dtype
            }
        )
        .merge(
            (
                df[f]
                .astype(pd.StringDtype())
                .value_counts(normalize=True)
                .reset_index()
                .assign(proportion=lambda df: df["proportion"] * 100)
            ),
            on=[f],
            how="left",
        )
        .assign(ctr=lambda df: 100 * df[pc] / df[pv])
        .assign(conversion_rate=lambda df: 100 * df["conversions"] / df[vis])
        .sort_values(by=[cr], ascending=False, ignore_index=True)
        .rename(columns={f: "feature_category"})
        .assign(feature_name=f)
        .assign(
            feature=lambda df: df["feature_name"].str.cat(
                df["feature_category"], sep="__"
            )
        )
    )
    return df_agg
