#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define general-purpose utilities."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,redefined-outer-name

import os
from typing import Union

import mlflow.sklearn
import pandas as pd
from IPython.display import display


def hilight_by_conditional(
    value: Union[float, int],
    low: Union[float, int] = 5,
    high: Union[float, int] = 10,
) -> str:
    """Hilight rows of a single column based on threshold limits."""
    if value > low and value < high:
        html_color = "background-color: #80FFff"
    elif value > high:
        html_color = "background-color: yellow"
    else:
        html_color = "background-color: antiquewhite"
    return html_color


def summarize_df(df: pd.DataFrame) -> None:
    """Show datatypes and count missing values in columns of DataFrame."""
    display(
        df.dtypes.rename("dtype")
        .to_frame()
        .merge(
            df.isna().sum().rename("missing").to_frame(),
            left_index=True,
            right_index=True,
            how="left",
        )
        .reset_index()
        .rename(columns={"index": "column"})
    )


def export_and_track(
    fpath: str, df: pd.DataFrame, filetype_msg: str, run_id: str
) -> None:
    """Export to disk and track using MLFlow."""
    df.to_parquet(fpath, index=False, engine="pyarrow", compression="gzip")
    print(f"Exported {filetype_msg} to file {os.path.basename(fpath)}")

    with mlflow.start_run(run_id=run_id) as _:
        mlflow.log_artifact(fpath)
    print(
        f"Logged {filetype_msg} as artifact in file {os.path.basename(fpath)}"
    )


def get_frac_outliers(s: pd.Series) -> float:
    """Calculate fraction of observations that are outliers."""
    Q1 = s.quantile(0.25)
    Q3 = s.quantile(0.75)
    IQR = Q3 - Q1
    num_outliers = ((s < (Q1 - 1.5 * IQR)) | (s > (Q3 + 1.5 * IQR))).sum()
    frac_outliers = 100 * num_outliers / len(s)
    return frac_outliers
