#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to generate audience profiles."""

# pylint: disable=invalid-name,dangerous-default-value,cell-var-from-loop
# pylint: disable=too-many-locals,unused-argument,bad-str-strip-call


from functools import reduce

import pandas as pd

import audience_size_helpers as ash


def get_profile_proportions(df: pd.DataFrame) -> pd.DataFrame:
    """Get visitor fraction for subset of features per audience group."""
    features, queries, conditions = [
        [
            "last_action",
            # "last_action",
            "last_action",
            "last_action",
            "last_action",
            "last_action",
            "medium",
            "added_to_cart",
            "day_of_week",
            "bounces",
        ],
        [
            "last_action == 'Add product(s) to cart'",
            # "last_action == 'Product detail_views'",
            "last_action == 'Completed purchase'",
            "last_action == 'Check out'",
            "last_action == 'Remove product(s) from cart'",
            "last_action == 'Click through of product lists'",
            "medium == 'referral'",
            "added_to_cart > 1",
            "(day_of_week == 1) | (day_of_week == 7)",
            "bounces == 1",
        ],
        [
            "last_action_added_to_cart",
            # "last_action_viewed_product_detail",
            "last_action_completed_purchase",
            "last_action_check_out",
            "last_action_removed_products_from_cart",
            "last_action_clicked_through_product_lists",
            "used_referral",
            "added_gt_1_to_cart",
            "weekend_visitors",
            "bounce_rate",
        ],
    ]
    dfs_proportion_by_aud = [
        df.groupby("maudience", as_index=False)
        .apply(lambda df: 100 * len(df.query(query_str)) / len(df))
        .rename(columns={None: condition})
        for query_str, condition in zip(queries, conditions)
    ]
    df_proportion_by_aud = (
        reduce(
            lambda df1, df2: pd.merge(df1, df2, on="maudience"),
            dfs_proportion_by_aud,
        )
        .set_index("maudience")
        .transpose()
        .reset_index()
        .rename(columns={"index": "stat"})
        .assign(stat_type="behavior")
        .assign(feature=features)
    )
    return df_proportion_by_aud


def get_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Get descriptive stats for subset of features per audience group."""
    df_profile_stats = df.groupby("maudience", as_index=False).agg(
        {
            "hour": ["mean"],
            "day_of_week": ["mean"],
            "source": [pd.Series.mode],
            "medium": [pd.Series.mode],
            "channelGrouping": [pd.Series.mode],
            "last_action": [pd.Series.mode],
            "browser": [pd.Series.mode],
            "os": [pd.Series.mode],
            "deviceCategory": [pd.Series.mode],
            "hits": ["mean", "max"],  #
            "promos_displayed": ["mean", "max"],
            "promos_clicked": ["mean", "max"],
            "product_views": ["mean", "max"],
            "product_clicks": ["mean", "max"],  #
            "pageviews": ["mean", "max"],  #
            "revenue": ["mean", "max"],
            "added_to_cart": ["mean", "max"],
        }
    )
    df_profile_stats.columns = [
        "__".join(column).rstrip("__")
        for column in df_profile_stats.columns.to_flat_index()
    ]
    stat = "stat"
    df_profile_stats = (
        df_profile_stats.set_index("maudience")
        .transpose()
        .reset_index()
        .rename(columns={"index": "stat"})
        .assign(stat_type=lambda x: x[stat].str.split("__", expand=True)[1])
        .assign(feature=lambda df: df[stat].str.split("__", expand=True)[0])
        .pipe(ash.move_cols_to_front, [stat, "stat_type"])
    )
    return df_profile_stats


def get_audience_profile(
    df: pd.DataFrame, audience_strategy: int = 1
) -> pd.DataFrame:
    """Generate profile for audience groups."""
    df_proportion_by_aud = get_profile_proportions(df)
    df_infer_aud_profile_stats = get_descriptive_stats(df)
    df_profile = pd.concat(
        [df_infer_aud_profile_stats, df_proportion_by_aud],
        ignore_index=True,
    ).pipe(
        ash.set_datatypes,
        {
            "feature": pd.StringDtype(),
            "stat_type": pd.StringDtype(),
            "stat": pd.StringDtype(),
        },
    )
    group_values_dict = {
        c: pd.StringDtype() for c in list(df_profile.select_dtypes("object"))
    }
    df_profile = pd.concat(
        [
            df_profile.pipe(ash.set_datatypes, group_values_dict),
            pd.DataFrame.from_records(
                [
                    {
                        "stat": "num_observations",
                        "stat_type": "behavior",
                        "High": len(df.query("maudience == 'High'")),
                        "Medium": len(df.query("maudience == 'Medium'")),
                        "Low": len(df.query("maudience == 'Low'")),
                        "feature": "all",
                    }
                ]
            ),
        ],
        ignore_index=True,
    ).assign(audience_strategy=audience_strategy)
    return df_profile
