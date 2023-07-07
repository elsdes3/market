#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to display Streamlit metrics."""

from typing import List

import pandas as pd
import streamlit as st

# pylint: disable=invalid-name


def show_streamlit_metrics(
    df_metrics: pd.DataFrame,
    metric_names_list: List[str],
    metric_titles_list: List[str],
) -> None:
    """Display list of Streamlit metrics."""
    cols = st.columns(len(metric_names_list))
    for st_col, metric_name, metric_title in zip(
        cols, metric_names_list, metric_titles_list
    ):
        metric_value, metric_chng = [
            df_metrics[metric_name].squeeze(),
            df_metrics[f"{metric_name}_pct_change"].squeeze(),
        ]
        if metric_name in ["visitors", "pageviews"]:
            metric_value /= 1_000
        if metric_name == "revenue":
            metric_value /= 1_000_000
        st_col.metric(
            metric_title, f"{metric_value:,.2f}", f"{metric_chng:,.2f}%"
        )
