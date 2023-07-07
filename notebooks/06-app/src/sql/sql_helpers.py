#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to execute BigQuery SQL to retrieve raw data."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments

import os
from datetime import datetime
from typing import Union

import pandas as pd
import pytz


def run_sql_query(
    query: str, gcp_project_id: str, gcp_creds: Union[os.PathLike, None]
) -> pd.DataFrame:
    """Run query on BigQuery and return results as pandas.DataFrame."""
    start_time = datetime.now(pytz.timezone("US/Eastern"))
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"Query execution start time = {start_time_str[:-3]}...", end="")
    df = pd.read_gbq(
        query,
        project_id=gcp_project_id,
        credentials=gcp_creds,
        dialect="standard",
        configuration={"query": {"useQueryCache": True}},
        # use_bqstorage_api=True,
    )
    end_time = datetime.now(pytz.timezone("US/Eastern"))
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    duration = end_time - start_time
    duration = duration.seconds + (duration.microseconds / 1_000_000)
    print(f"done at {end_time_str[:-3]} ({duration:.3f} seconds).")
    print(f"Query returned {len(df):,} rows")
    return df
