#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Create dashboard for client to get insights and propensity predictions."""

import os
from calendar import month_name
from glob import glob
from typing import List

import pandas as pd
import streamlit as st

import src.st_utils as ut
from src.data.data import export_to_xlsx, get_data
from src.metrics.st_metrics import show_streamlit_metrics

# pylint: disable=invalid-name

# Specify layout, Browser tab title and icon
ut.set_page_config(
    title="Propensity and Analytics Dashboard",
    layout="centered",
    menu_items={
        "Get Help": "https://github.com/elsdes3/market/issues",
        "Report a bug": "https://github.com/elsdes3/market/pulls",
        "About": (
            "Visualize tracking data and factors important to predicting "
            "propensity, for first-time visitors during production period"
        ),
    },
)

ut.configure_page()


def show_env_vars() -> None:
    """Use Streamlit to show all available environment variables."""
    df_env_vars = (
        pd.DataFrame.from_records([{k: v for k, v in os.environ.items()}])
        .transpose()
        .sort_index()
        .reset_index()
        .rename(columns={"index": "env_var_name", 0: "value"})
        .set_index(["env_var_name"])
    )
    st.write(df_env_vars)


def show_workdir_contents(workdir_contents_list: List[str]) -> None:
    """Use Streamlit to show contents of working directory."""
    st.markdown("Working directory contains following contents")
    df_workdir_contents = pd.Series(
        workdir_contents_list, name="filename"
    ).to_frame()
    st.dataframe(df_workdir_contents, hide_index=True)


HOME_DIR = os.path.expanduser("~") if not os.path.exists("/app") else "/app"
gcp_keys_dir = os.path.join(HOME_DIR, "gcp_keys")

PROJ_ROOT_DIR = os.path.join(os.getcwd())
st.markdown("## Environment Variables")
show_env_vars()
st.markdown("## Contents of working directory")
local_dirs = [os.path.basename(f) for f in glob(f"{PROJ_ROOT_DIR}/*")]
show_workdir_contents(local_dirs)

# GCP resources
gbq_dataset_id = "mydemo2asdf"
gbq_table_id_summary = "monthly_summary"
gbq_table_id_cohorts = "audience_cohorts"
audience_strategy_mapper = {1: "Multi-Group", 2: "Single Group"}

gcp_proj_id = os.environ["GCP_PROJECT_ID"]
gbq_summary_table_id_fully_resolved = (
    f"{gcp_proj_id}.{gbq_dataset_id}.{gbq_table_id_summary}"
)
gbq_table_fully_resolved_cohorts = (
    f"{gcp_proj_id}.{gbq_dataset_id}.{gbq_table_id_cohorts}"
)

st.markdown("## Tracking Metrics and Audience Cohorts")
if os.path.exists(gcp_keys_dir):
    path_check = st.success(
        f"Found raw data path: {os.path.abspath(gcp_keys_dir)}, "
        "using service account access key"
    )
else:
    path_check = st.error(
        f"Did not find raw data path: {os.path.abspath(gcp_keys_dir)}, "
        "not using service account access key"
    )

dtypes_dict_summary = {
    "month": pd.Int8Dtype(),
    "audience_strategy": pd.StringDtype(),
    "split_type": pd.StringDtype(),
    "return_purchasers": pd.Int16Dtype(),
    "revenue": pd.Float32Dtype(),
    "visitors": pd.Int16Dtype(),
    "pageviews": pd.Int32Dtype(),
    "time_on_site": pd.Float32Dtype(),
    "channelGrouping": pd.StringDtype(),
    "deviceCategory": pd.StringDtype(),
    "browser": pd.StringDtype(),
    "os": pd.StringDtype(),
    "bounce_rate": pd.Float32Dtype(),
    "conversion_rate": pd.Float32Dtype(),
    "product_clicks_rate": pd.Float32Dtype(),
    "add_to_cart_rate": pd.Float32Dtype(),
    "visitor_type": pd.StringDtype(),
    "visitors_pct_change": pd.Float32Dtype(),
    "revenue_pct_change": pd.Float32Dtype(),
    "pageviews_pct_change": pd.Float32Dtype(),
    "time_on_site_pct_change": pd.Float32Dtype(),
    "bounce_rate_pct_change": pd.Float32Dtype(),
    "conversion_rate_pct_change": pd.Float32Dtype(),
    "product_clicks_rate_pct_change": pd.Float32Dtype(),
    "add_to_cart_rate_pct_change": pd.Float32Dtype(),
}
df_summary_infer = get_data(
    f"""
    SELECT *
    FROM {gbq_summary_table_id_fully_resolved}
    WHERE split_type = 'Infer'
    """,
    {"audience_strategy": audience_strategy_mapper},
    dtypes_dict_summary,
    gcp_keys_dir,
    data_type="all summary",
)

st.markdown("### Aggregated Monthly Metrics for Site Traffic")
most_recent_month = month_name[1:][df_summary_infer["month"].iloc[0] - 1]
ut.print_custom_text(
    (
        "Google Analytics metrics during month covering inference period "
        f"({most_recent_month})"
    ),
    font_size=20,
    font_color="rgb(100, 149, 237)",
)
metrics_top = [
    "visitors",
    "revenue",
    "time_on_site",
    "pageviews",
]
metric_titles_top = [
    "Visitors (K)",
    "Revenue (USD, millions)",
    "Avg. time on site (min)",
    "Page views (K)",
]
metrics_bottom = ["product_clicks_rate", "add_to_cart_rate", "bounce_rate"]
metric_titles_bottom = [
    "Product List CTR (%)",
    "Add-to-Cart Rate (%)",
    "Bounce Rate (%)",
]
for metrics, titles in zip(
    [metrics_top, metrics_bottom], [metric_titles_top, metric_titles_bottom]
):
    show_streamlit_metrics(df_summary_infer, metrics, titles)

st.markdown("### Download Predicted Audience Cohorts")
dtypes_dict_cohort = {
    "infer_month": pd.StringDtype(),
    "fullvisitorid": pd.StringDtype(),
    "visitId": pd.StringDtype(),
    "visitNumber": pd.Int8Dtype(),
    "quarter": pd.Int8Dtype(),
    "month": pd.Int8Dtype(),
    "day_of_month": pd.Int8Dtype(),
    "day_of_week": pd.Int8Dtype(),
    "hour": pd.Int8Dtype(),
    "minute": pd.Int8Dtype(),
    "second": pd.Int8Dtype(),
    "source": pd.CategoricalDtype(),  #
    "medium": pd.CategoricalDtype(),  #
    "channelGrouping": pd.CategoricalDtype(),  #
    "hits": pd.Int16Dtype(),
    "bounces": pd.Int32Dtype(),  #
    "last_action": pd.CategoricalDtype(),  #
    "promos_displayed": pd.Int32Dtype(),
    "promos_clicked": pd.Int32Dtype(),
    "product_views": pd.Int32Dtype(),
    "product_clicks": pd.Int32Dtype(),
    "pageviews": pd.Int32Dtype(),
    "time_on_site": pd.Int32Dtype(),
    "browser": pd.CategoricalDtype(),  #
    "os": pd.CategoricalDtype(),  #
    "revenue": pd.Float32Dtype(),
    "added_to_cart": pd.Int32Dtype(),
    "deviceCategory": pd.CategoricalDtype(),  #
    "score": pd.Float32Dtype(),
    "predicted_score_label": pd.BooleanDtype(),
    "maudience": pd.StringDtype(),
    "cohort": pd.StringDtype(),
    "audience_strategy": pd.StringDtype(),
}
df_dev_cohorts = get_data(
    f"""
        SELECT * EXCEPT (made_purchase_on_future_visit, split_type)
        FROM {gbq_table_fully_resolved_cohorts}
        WHERE split_type = 'infer'
        """,
    {"audience_strategy": audience_strategy_mapper},
    dtypes_dict_cohort,
    gcp_keys_dir,
    data_type="cohorts",
)
df_xlsx = export_to_xlsx(df_dev_cohorts)
ut.print_custom_text(
    "Inference data with predicted propensity and audience cohort",
    font_size=20,
    font_color="rgb(100, 149, 237)",
)
show_df = st.expander(":blue[Preview] data")
ut.print_custom_text("Assumptions")
st.markdown(
    """
    The preferred marketing strategy was to use three audience groups.
    So, first-time visitors were divided into three groups based on their
    predicted propensity to make a purchase on a return visit to the store.
    """
)
ut.print_custom_text("Notes")
st.markdown(
    """
    > This data can be directly used to access the candidate marketing
    audience (the `maudience` column), test and control cohorts (`cohort`)
    assumed audience segmentation strategy (`audience_strategy`). The
    `score` column gives the numerical predicted propensity and the
    `predicted_score_label` indicates the predicted outcome for the
    visitor (`False` indicates the visitor is not predicted to make a
    purchase on a return visit, while `True` indicates the opposite).
    The audience segmentation strategy indicates the number of groups
    to which the visitors were assigned. Per the assumption, three such
    groups were used. So, for a :blue[*Multi-Group*] strategy, visitors
    were placed into three groups based on their predicted propensity to
    make a purchase on a return visit. So, the audience consists of three
    groups and cohorts are created from all three groups. For
    :blue[*Single Group*], first-time visitors were again placed into
    three groups, but only the group in the top third in terms of
    predicted propensity was chosen for creating test and control cohorts.
    """
)
with show_df:
    st.caption("First five rows of data available for download")
    st.table(df_dev_cohorts.head(5).set_index("infer_month"))
_ = st.download_button(
    label=":floppy_disk: Download data as .XLSX file",
    data=df_xlsx,
    file_name="Audience_cohorts_predictions.xlsx",
    mime="application/vnd.ms-excel",
)
