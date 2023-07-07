#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to upload to BigQuery."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,broad-except

import pandas as pd
from google.cloud import bigquery


def create_bq_table(table_id_full: str, client) -> None:
    """Create BigQuery table."""
    table = bigquery.Table(table_id_full)
    try:
        table = client.create_table(table)
        print(
            "Created table named "
            f"{table.project}.{table.dataset_id}.{table.table_id}"
        )
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Found existing table {table_id_full}")
        else:
            print(str(e))


def append_df_to_bq_table(
    df: pd.DataFrame,
    job_config: bigquery.LoadJobConfig,
    table_id_full: str,
    client,
) -> None:
    """."""
    cols_to_use = [f.name for f in job_config.schema]
    assert sorted(list(df)) == sorted(cols_to_use)

    job = client.load_table_from_dataframe(
        df, destination=table_id_full, job_config=job_config
    )
    _ = job.result()
    print("Completed upload")

    table = client.get_table(table_id_full)
    print(
        f"Found {table.num_rows:,} rows and {len(table.schema):,} columns in "
        f"table {table.dataset_id}.{table.table_id}"
    )
