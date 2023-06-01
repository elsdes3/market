#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to manage MLFlow models."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument

import json
import os
from glob import glob
from typing import List, Union

import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from sklearn.pipeline import Pipeline


def get_all_deployment_candidate_models() -> pd.DataFrame:
    """Get all MLFlow deployment candidate models from model registry."""
    client = MlflowClient(tracking_uri=mlflow.get_tracking_uri())
    df = pd.concat(
        [
            pd.DataFrame.from_dict(
                dict(
                    name=mlflow_model_obj.name,
                    description=mlflow_model_obj.description,
                    run_id=mlflow_model_obj.run_id,
                    tags=mlflow_model_obj.tags,
                    version=mlflow_model_obj.version,
                ),
                orient="index",
            ).transpose()
            for mlflow_model_obj in client.search_model_versions()
            if mlflow_model_obj.tags
        ],
        ignore_index=True,
    ).assign(
        score=lambda df: (
            df["description"].str.split("score of ", expand=True)[1]
        ).astype(pd.Float32Dtype())
    )
    return df


def get_best_deployment_candidate_model(df: pd.DataFrame) -> str:
    """Retrieve name of the best deployment candidate model."""
    df = df.sort_values(by=["score"], ascending=False)
    best_run_model_name = df.head(1).squeeze()["name"]
    return best_run_model_name


def get_data_for_run_id(df: pd.DataFrame, file_prefix: str) -> pd.DataFrame:
    """Get data associated with a run ID."""
    run_artifacts_parent_dir = mlflow.artifacts.download_artifacts(
        run_id=df.squeeze()["run_id"]
    )
    run_processed_data_fpath = glob(
        os.path.join(
            run_artifacts_parent_dir, f"{file_prefix}__run_*.parquet.gzip"
        )
    )[-1]
    df = pd.read_parquet(run_processed_data_fpath)
    return df


def get_all_experiment_runs() -> pd.DataFrame:
    """Get all experiment runs."""
    client = MlflowClient(tracking_uri=mlflow.get_tracking_uri())
    experiments = client.search_experiments(filter_string="name != 'Default'")
    df = pd.concat(
        [
            pd.read_parquet(
                glob(f"mlruns/{row['run_id']}/*/ml__run_*.parquet.gzip")[0]
            )
            for experiment in experiments
            for _, row in mlflow.search_runs(
                experiment_ids=[experiment.experiment_id]
            ).iterrows()
        ],
        ignore_index=True,
    ).rename(columns={"experiment": "experiment_id"})
    return df


def get_best_experiment_run(
    df: pd.DataFrame, query_filter: str, metric: Union[str, None] = None
) -> pd.Series:
    """Get best experiment run using filter and/or metric."""
    df_best = df.query(query_filter)
    if metric:
        df_best = df_best.sort_values(by=[metric], ascending=False)
    df_best_expt_run = df_best.head(1).squeeze()
    return df_best_expt_run


def get_single_registered_model(filter_str: str) -> pd.DataFrame:
    """Get single registered model using filter."""
    client = MlflowClient(tracking_uri=mlflow.get_tracking_uri())
    df_model = pd.DataFrame.from_records(
        [
            {
                "name": rm.name,
                "run_id": rm.latest_versions[-1].run_id,
                "description": rm.latest_versions[-1].description,
                "source": rm.latest_versions[-1].source,
                "version": rm.latest_versions[-1].version,
                "status": rm.latest_versions[-1].status,
            }
            for rm in client.search_registered_models()
        ]
    ).query(filter_str)
    return df_model


def check_data_per_best_expt_run(
    df_dep_cand_model: pd.DataFrame,
    df_all_data: pd.DataFrame,
    X_infer: pd.DataFrame,
    label_column: str,
) -> None:
    """Run sanity checks on data using metadata from best experiment run."""
    # Get run ID associated with the best deployment candidate model
    best_run_id = df_dep_cand_model.head(1).squeeze()["run_id"]

    # Get all experiment runs
    df_expt_runs = get_all_experiment_runs()

    # Get outputs of best experiment run
    df_best_expt_run = get_best_experiment_run(
        df_expt_runs,
        f"(experiment_run_type == 'parent') & (run_id == '{best_run_id}')",
        None,
    )

    # Get metadata for observations (start and end date of training data) &
    # features (column names) associated with best experiment run
    best_train_start_date, best_test_end_date = [
        df_best_expt_run[c] for c in ["train_start_date", "test_end_date"]
    ]
    cols_best_expt_run = json.loads(df_best_expt_run["column_names"])

    # Verify features in all available data and inference data match columns
    # associated with best experiment run
    assert cols_best_expt_run == list(df_all_data)
    assert set(cols_best_expt_run) - set([label_column]) == set(list(X_infer))

    # Verify observations in all available data match start and end dates
    # associated with best experiment run
    data_start_date, data_end_date = [
        df_all_data["visitStartTime"].dt.date.min().strftime("%Y%m%d"),
        df_all_data["visitStartTime"].dt.date.max().strftime("%Y%m%d"),
    ]
    assert data_start_date == best_train_start_date
    assert data_end_date == best_test_end_date


def make_inference(
    model: Pipeline, X: pd.DataFrame, y_pred_name: str
) -> List[pd.Series]:
    """Make inference predictions using trained model."""
    y_pred = pd.Series(
        model.predict(X), index=X.index, dtype=pd.Int8Dtype(), name=y_pred_name
    )
    y_pred_proba = pd.Series(
        model.predict_proba(X)[:, 1], index=X.index, name=y_pred_name
    )
    return [y_pred, y_pred_proba]
