#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Create dashboard page to visualize analytics metrics tracking over time."""

import os

import altair as alt
import pandas as pd
import streamlit as st

import src.utils.st_utils as ut
import src.visualization.dash_helpers as dh
from src.data.data import get_data

# pylint: disable=invalid-name

# Specify layout, Browser tab title and icon
ut.set_page_config(
    title="View Audience Profile",
    layout="centered",
    menu_items={
        "Get Help": "https://github.com/elsdes3/market/issues",
        "Report a bug": "https://github.com/elsdes3/market/pulls",
        "About": "Visualize profile of predicted audience groupings",
    },
)

ut.configure_page()

HOME_DIR = os.path.expanduser("~") if not os.path.exists("/app") else "/app"
gcp_keys_dir = os.path.join(HOME_DIR, "gcp_keys")

# GCP resources
gbq_dataset_id = "mydemo2asdf"
gbq_table_id_profiles = "audience_profiles"
gbq_table_id_feats_imp = "audience_feats_imp"
gbq_table_id_cat_feats_kpis = "categorical_features_kpis"
audience_strategy_mapper = {1: "Multi-Group", 2: "Single Group"}

gcp_proj_id = os.environ["GCP_PROJECT_ID"]
gbq_table_fully_resolved_profiles = (
    f"{gcp_proj_id}.{gbq_dataset_id}.{gbq_table_id_profiles}"
)
gbq_table_fully_resolved_feats_imp = (
    f"{gcp_proj_id}.{gbq_dataset_id}.{gbq_table_id_feats_imp}"
)
gbq_table_fully_resolved_cat_feat_kpis = (
    f"{gcp_proj_id}.{gbq_dataset_id}.{gbq_table_id_cat_feats_kpis}"
)

st.markdown("## Profiles of Predicted Audience")
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

dtypes_dict_feats_imp = {
    "audience_strategy": pd.StringDtype(),
    "num_observations": pd.Int16Dtype(),
    "stat": pd.StringDtype(),
    "maudience": pd.StringDtype(),
    "value": pd.StringDtype(),
}
dtypes_profiles = {
    "Stat_Expanded": pd.StringDtype(),
    "Audience_Strategy": pd.StringDtype(),
    "High": "float",
    "Medium": "float",
    "Low": "float",
}
dtypes_dict_categorical_kpis = {
    "feature_name": pd.StringDtype(),
    "feature_category": pd.StringDtype(),
    "variable": pd.StringDtype(),
    "value": pd.Float32Dtype(),
}


with st.sidebar:
    st.markdown("## Propensity Group")
    maudience = st.sidebar.selectbox(
        "Select audience group",
        ("High", "Medium", "Low"),
        label_visibility="collapsed",
    )

    st.markdown("## Historical KPIs")
    feature = st.sidebar.selectbox(
        "Select feature",
        (
            "os",
            "source",
            "browser",
            "medium",
            "channelGrouping",
            "deviceCategory",
            "last_action",
        ),
        label_visibility="collapsed",
    )

df_feats_imp = get_data(
    f"""
        SELECT *
        FROM {gbq_table_fully_resolved_feats_imp}
        WHERE maudience = '{maudience}'
        ORDER BY audience_strategy, maudience
        """,
    {"audience_strategy": audience_strategy_mapper},
    dtypes_dict_feats_imp,
    gcp_keys_dir,
    data_type="profiles",
)
df_development_agg = get_data(
    f"""
    SELECT feature_name,
           feature_category,
           variable,
           value
    FROM {gbq_table_fully_resolved_cat_feat_kpis}
    WHERE variable IN ('CTR', 'Conversion Rate')
    AND feature_name = '{feature}'
    """,
    {},
    dtypes_dict_categorical_kpis,
    gcp_keys_dir,
    data_type="categoricals_kpis",
)

st.markdown("### Useful factors to predict return purchase propensity")
tooltip = [
    alt.Tooltip("stat", title="Feature"),
    alt.Tooltip("audience_strategy", title="Audience Strategy"),
    alt.Tooltip("maudience", title="Audience Group"),
    alt.Tooltip("num_observations", title="Observations needed", format=","),
    alt.Tooltip("value", title="Importance", format=",.3f"),
]
chart = dh.plot_feature_importances(
    data=df_feats_imp,
    y_label_width=600,
    axis_label_fontsize=16,
    tooltip=tooltip,
    interactive=False,
    bar_color="#525252",
    show_x_ticks=False,
    fig_size=dict(width=600, height=300),
)

ut.print_custom_text(
    (
        "Top features for first-time visitors predicted to have "
        f"{maudience} propensity to purchase on return"
    ),
    font_size=16,
    font_color="rgb(100, 149, 237)",
)
st.altair_chart(chart, theme="streamlit", use_container_width=True)

st.markdown("### Historical KPIs for Categorical Features")
tooltip = [
    alt.Tooltip("feature_name:N", title="Categorical Feature"),
    alt.Tooltip("feature_category:N", title="Feature Sub-Category"),
    alt.Tooltip("variable:N", title="Rate Type"),
    alt.Tooltip("value:N", title="Rate (%)", format=".3f"),
]
ytitle_cats_kpis = {
    "os": {
        "ptitle": (
            "Linux and Mac operating systems give the best combination of "
            "KPIs"
        ),
        "expanded": "Operating Systems",
    },
    "source": {
        "ptitle": "Direct traffic gives best combination of KPIs",
        "expanded": "Traffic Source",
    },
    "browser": {
        "ptitle": "Chrome offers best combination of KPIs among web browsers",
        "expanded": "Browser used to access store site",
    },
    "medium": {
        "ptitle": (
            "Traffic reaching from CPM, referral or no medium gives the best "
            "combination of KPIs"
        ),
        "expanded": "Traffic Medium",
    },
    "channelGrouping": {
        "ptitle": (
            "Referral, direct or display channel shows the best combination "
            "of KPIs"
        ),
        "expanded": "Channel",
    },
    "deviceCategory": {
        "ptitle": "Desktop devices give best combination of KPIs",
        "expanded": "Type of Electronic Device",
    },
    "last_action": {
        "ptitle": (
            "Ending a first visit with a Check Out or Add To/Remove from "
            "Cart gives best KPIs"
        ),
        "expanded": "Last Action performed at end of first visit",
    },
}
chart = dh.plot_stacked_bar_chart(
    data=df_development_agg,
    xvar="feature_category",
    yvar="value",
    color_by_col="variable",
    colors={"CTR": "#cccccc", "Conversion Rate": "red"},
    show_title=True,
    show_legend=True,
    ptitle_str=ytitle_cats_kpis[feature]["ptitle"],
    tooltip=[
        alt.Tooltip("feature_name:N", title="Categorical Feature"),
        alt.Tooltip("feature_category:N", title="Feature Sub-Category"),
        alt.Tooltip("variable:N", title="Rate Type"),
        alt.Tooltip("value:N", title="Rate (%)", format=".3f"),
    ],
    x_label_height=400,
    axis_label_fontsize=16,
    title_fontsize=18,
    title_fontweight="normal",
    x_tick_label_angle=-90,
    fig_size=dict(width=400, height=450),
)
ut.print_custom_text(
    f"KPIs by {ytitle_cats_kpis[feature]['expanded']}",
    font_size=16,
    font_color="rgb(100, 149, 237)",
)
st.altair_chart(chart, theme="streamlit", use_container_width=True)

st.caption("Data updated monthly")
st.caption("Last updated: April 1, 2017")
st.caption("Source: Google Merchandise store analytics tracking data")

st.markdown("### Recommendations to Maximize Campaign Response")
ut.print_custom_text("Context")
st.markdown(
    """
    In order to best spend available marketing budget this allows greater
    flexibility in how customized a campaign response can be customized by
    using a different marketing approach with a customer that is predicted
    to have a high, medium or low propensity to make a return purchase.
    """
)
ut.print_custom_text("Recommendations Per Predicted Audience Group")
st.markdown(
    """
    Based on
    1. discoveries made from exploring the data
    2. the ML model's most important features for predicting whether a visitor
    will make a return purchase

    we should target the following visitor profiles to maximize campaign
    response
    """
)

high = st.expander(":green[High Propensity Visitor Profile]")
with high:
    st.markdown(
        """
        1. reached the store site using a paid search
        2. used an uncommonly used browser
        3. used one of the following operating systems
           - FreeBSD
           - Nokia-based OS
        3. interacted with content on the store site

        with an :blue[emphasis] on visitors who accessed the site from an
        uncommonly used browser.
        """
    )
medium = st.expander("Medium Propensity Visitor Profile")
with medium:
    st.markdown(
        """
        1. interacted with content on the store site
        2. used one of the following frequently used operating systems
           - Macintosh
           - Chrome OS
        3. used one of the following infrequently used operating systems
           - Nintendo WII
           - Firefox OS
        4. used an undetermined medium to access the store site
        5. reached store site using a google search

        with an :blue[emphasis] on
        - visitors who used a Mac-based operating system to access the store
        site
        - Chrome OS users (i.e. chromebook users)
        """
    )
low = st.expander(":violet[Low Propensity Visitor Profile]")
with low:
    st.markdown(
        """
        1. reached the store site by
           - sources other than google search
           - directly entering URL into web browser
        2. used one of the following OSes to access the store site
           - SunOS
           - Macintosh OS
        3. used an affiliate or undetermined medium to access the store site
        4. did not bounce from the store site

        with an :blue[emphasis] on
        - visitors who reached the site during their first visit by
           - sources other than google search
           - directly entering URL into web browser
        - visitors who used a Mac-based operating system to access the store
        site
        - did not bounce from the site
        """
    )
ut.print_custom_text("Notes")
st.markdown(
    """
    The recommended :blue[emphasis] is based on factors that produced a good
    combination of KPIs (CTR and conversion rate) among first-time visitors
    in the closest available month of historical data.
    """
)
