#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Create dashboard page to visualize analytics metrics tracking over time."""

import os
from calendar import month_name

import altair as alt
import pandas as pd
import streamlit as st

import src.utils.st_utils as ut
import src.visualization.dash_helpers as dh
from src.data.data import get_data

# pylint: disable=invalid-name

# Specify layout, Browser tab title and icon
ut.set_page_config(
    title="Plot Analytics Metrics over Time",
    layout="wide",
    menu_items={
        "Get Help": "https://github.com/elsdes3/market/issues",
        "Report a bug": "https://github.com/elsdes3/market/pulls",
        "About": "Visualize tracking data monthly and daily",
    },
)

ut.configure_page()

HOME_DIR = os.path.expanduser("~") if not os.path.exists("/app") else "/app"
gcp_keys_dir = os.path.join(HOME_DIR, "gcp_keys")

# GCP resources
gbq_dataset_id = "mydemo2asdf"
gbq_table_id_summary = "monthly_summary"
gbq_table_id_daily_perf = "daily_summary"
audience_strategy_mapper = {1: "Multi-Group", 2: "Single Group"}

gcp_proj_id = os.environ["GCP_PROJECT_ID"]
gbq_summary_table_id_fully_resolved = (
    f"{gcp_proj_id}.{gbq_dataset_id}.{gbq_table_id_summary}"
)
gbq_daily_perf_combo_table_id_fully_resolved = (
    f"{gcp_proj_id}.{gbq_dataset_id}.{gbq_table_id_daily_perf}"
)

st.markdown("## Trends in Google Analytics Metrics")
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
st.warning("This page is best viewed in fullscreen", icon="⚠️")

dtypes_dict_summary = {
    "return_purchasers": pd.Int16Dtype(),
    "revenue": pd.Float32Dtype(),
    "visitors": pd.Int16Dtype(),
    "pageviews": pd.Int32Dtype(),
    "time_on_site": pd.Float32Dtype(),
    "bounce_rate": pd.Float32Dtype(),
    "conversion_rate": pd.Float32Dtype(),
    "product_clicks_rate": pd.Float32Dtype(),
    "add_to_cart_rate": pd.Float32Dtype(),
    "visitors_pct_change": pd.Float32Dtype(),
    "revenue_pct_change": pd.Float32Dtype(),
    "pageviews_pct_change": pd.Float32Dtype(),
    "time_on_site_pct_change": pd.Float32Dtype(),
    "bounce_rate_pct_change": pd.Float32Dtype(),
    "conversion_rate_pct_change": pd.Float32Dtype(),
    "product_clicks_rate_pct_change": pd.Float32Dtype(),
    "add_to_cart_rate_pct_change": pd.Float32Dtype(),
}

with st.sidebar:
    st.markdown("## Analytics Metric")
    metric = st.radio(
        "Select metric",
        [
            "Visitors",
            "Revenue",
            "Add to Cart Rate",
            "Bounce Rate",
            "Conversion Rate",
            "Product Clicks Rate",
            "Time on Site",
            "Pageviews",
        ],
        key="visibility",
        label_visibility="collapsed",
        disabled=False,
        horizontal=False,
    )
    yvar = metric.replace(" ", "_").lower()

df_summary = get_data(
    f"""
    SELECT month,
           audience_strategy,
           split_type,
           {yvar},
           {yvar}_pct_change,
           {yvar}_pct_change_gt_0
    FROM {gbq_summary_table_id_fully_resolved}
    """,
    {
        "audience_strategy": audience_strategy_mapper,
        "month": dict(zip(list(range(1, 12 + 1)), month_name[1:])),
    },
    {
        "month": pd.StringDtype(),
        "audience_strategy": pd.StringDtype(),
        yvar: dtypes_dict_summary[yvar],
        f"{yvar}_pct_change_gt_0": pd.BooleanDtype(),
    },
    gcp_keys_dir,
    data_type="all summary",
    custom_sort_single_col={
        "month": [
            "September",
            "October",
            "November",
            "December",
            "January",
            "February",
            "March",
        ]
    },
)
if yvar not in ["conversion_rate", "product_views", "visitors", "pageviews"]:
    df_daily_summary_aud = get_data(
        f"""
            SELECT maudience,
                   date,
                   {yvar}
            FROM {gbq_daily_perf_combo_table_id_fully_resolved}
            WHERE agg_type != 'overall'
            """,
        {},
        {"maudience": pd.StringDtype(), yvar: pd.Float32Dtype()},
        gcp_keys_dir,
        date_col="date",
        data_type="daily summary by audience group",
    )

# Monthly charts
ytitle_month = {
    "visitors": "Visitors",
    "revenue": "Revenue (USD)",
    "add_to_cart_rate": "Fraction of Visitors that Added Item(s) to Cart (%)",
    "bounce_rate": "Bounce Rate (%)",
    "conversion_rate": "Conversion Rate (%)",
    "product_clicks_rate": "Product List Clickthrough Rate (%)",
    "time_on_site": "Average time spent on store website (minutes)",
    "pageviews": "Number of pages viewed during visit",
}
chart_month = dh.plot_statistic_bar_chart_combo(
    data=df_summary,
    yvar=yvar,
    color_by_col="split_type:N",
    marker_size=80,
    marker_colors=["red", "green"],
    marker_values=[False, True],
    x_axis_sort=df_summary["month"].tolist(),
    ptitle=ytitle_month[yvar],
    axis_label_fontsize=16,
    title_fontsize=20,
    title_fontweight="normal",
    ptitle_vertical_offset=-1,
    fig_size_bars=dict(width=600, height=300),
    fig_size_lines=dict(width=600, height=125),
)

# Daily charts
ytitle_daily = {
    "bounce_rate": (
        "Bounce rate for all audience groups within non-holiday range during "
        "development"
    ),
    "product_clicks_rate": (
        "Product CTR for all audience groups within 95% c.i. during "
        "development"
    ),
    "add_to_cart_rate": (
        "Add-to-cart rate for all audience groups within 95% c.i. during "
        "development"
    ),
    "time_on_site": (
        "Average time spent on store site for all audience groups within 95% "
        "c.i. during development"
    ),
    "revenue": (
        "First-visit revenue for all audience groups within post-holiday "
        "range"
    ),
}
daily_legend_params = dict(
    direction="horizontal", orient="bottom", titleAnchor="start"
)
if yvar not in ["conversion_rate", "product_views", "visitors", "pageviews"]:
    chart_daily_by_aud = dh.plot_time_dependent_scatter_chart(
        df_daily_summary_aud,
        yvar=yvar,
        line_thickness=0.5,
        color_by_col="maudience",
        ptitle_str=ytitle_daily[yvar],
        axis_title_fontsize=20,
        axis_label_fontsize=16,
        axis_label_angle=0,
        axis_tick_label_color="#757575",
        marker_order=["Low", "High", "Medium", "Development"],
        marker_colors=["#fbb4ae", "darkred", "#c7e9c0", "#bdbdbd"],
        marker_size=100,
        show_title=True,
        show_legend=True,
        legend_params={
            "scatter": daily_legend_params,
            "area": daily_legend_params,
            "line": daily_legend_params,
        },
        tooltip=[
            alt.Tooltip("maudience", title="Audience group"),
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip(f"{yvar}:Q", title=metric, format=",.2f"),
        ],
        ci_level=0.95,
        fig_size=dict(width=800, height=350),
    )
else:
    chart_daily_by_aud = None

# Show charts
col1, col2 = st.columns([6, 6])
with col1:
    ut.print_custom_text(
        (
            "End-of-month and month-over-month GA360 Metrics covering all "
            "tracking data used"
        ),
        font_size=22,
        font_color="rgb(100, 149, 237)",
    )
    st.altair_chart(chart_month, theme="streamlit", use_container_width=True)
    ut.print_custom_text("Notes")
    st.markdown(
        "> Tracking metrics reflect seasonality of store sales. Visits are "
        "retrieved for US visitors only. Revenue from first-time visitors "
        "increases leading up to December holiday season, with a peak in "
        "November for the [US Thanksgiving](https://www.calendardate.com/"
        "thanksgiving_2016.htm) holiday. Except for page views and bounce "
        "rate, other metrics show the same trend."
    )
with col2:
    ut.print_custom_text(
        "Daily GA360 Metrics covering all tracking data",
        font_size=22,
        font_color="rgb(100, 149, 237)",
    )
    if not chart_daily_by_aud:
        ut.print_custom_text("Please select another metric")
    else:
        st.altair_chart(
            chart_daily_by_aud, theme="streamlit", use_container_width=True
        )
        ut.print_custom_text("Notes")
        st.markdown(
            "> Dates are offset backwards by one day due to technical "
            "issue with the plotting framework used ([1](https://discuss."
            "streamlit.io/t/altair-time-transforms-are-off/19453/6), [2]"
            "(https://github.com/altair-viz/altair/issues/2540)). Future "
            "versions of dashboard will explore workarounds."
        )
st.caption("Data updated monthly")
st.caption("Last updated: April 1, 2017")
st.caption("Source: Google Merchandise store analytics tracking data")
