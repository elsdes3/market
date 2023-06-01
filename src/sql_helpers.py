#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to execute BigQuery SQL to retrieve raw data."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments

import os
from datetime import datetime

import pandas as pd
import pytz
from IPython.display import display


def get_sql_query(
    split_start_date: str,
    split_end_date: str,
    train_split_start_date: str,
    test_split_end_date: str,
) -> str:
    """Assemble query to retrieve attributes about first visits."""
    query_str = f"""
            WITH
            -- Step 1. get visitors with a return visit
            returning_visitors AS (
                 SELECT fullvisitorid,
                        IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, True, False) AS made_purchase_on_future_visit
                 FROM `data-to-insights.ecommerce.web_analytics`
                 WHERE date BETWEEN '{train_split_start_date}' AND '{test_split_end_date}'
                 AND geoNetwork.country = 'United States'
                 GROUP BY fullvisitorid
            ),
            -- Steps 2. and 3. get attributes of the first visit
            first_visit_attributes AS (
                SELECT -- =========== GEOSPATIAL AND TEMPORAL ATTRIBUTES OF VISIT ===========
                       geoNetwork.country,
                       EXTRACT(QUARTER FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS quarter,
                       EXTRACT(MONTH FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS month,
                       EXTRACT(DAY FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS day_of_month,
                       EXTRACT(DAYOFWEEK FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS day_of_week,
                       EXTRACT(HOUR FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS hour,
                       EXTRACT(MINUTE FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS minute,
                       EXTRACT(SECOND FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS second,
                       -- =========== VISIT AND VISITOR METADATA ===========
                       fullvisitorid,
                       visitId,
                       visitNumber,
                       DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific') AS visitStartTime,
                       -- =========== SOURCE OF SITE TRAFFIC ===========
                       -- source of the traffic from which the visit was initiated
                       trafficSource.source,
                       -- medium of the traffic from which the visit was initiated
                       trafficSource.medium,
                       -- referring channel connected to visit
                       channelGrouping,
                       -- =========== VISITOR ACTIVITY ===========
                       -- total number of hits
                       (CASE WHEN totals.hits > 0 THEN totals.hits ELSE 0 END) AS hits,
                       -- number of bounces
                       (CASE WHEN totals.bounces > 0 THEN totals.bounces ELSE 0 END) AS bounces,
                       -- action performed during first visit
                       CAST(h.eCommerceAction.action_type AS INT64) AS action_type,
                       -- page views
                       IFNULL(totals.pageviews, 0) AS pageviews,
                       -- time on the website
                       IFNULL(totals.timeOnSite, 0) AS time_on_site,
                       -- whether add-to-cart was performed during visit
                       (CASE WHEN CAST(h.eCommerceAction.action_type AS INT64) = 3 THEN 1 ELSE 0 END) AS added_to_cart,
                       -- =========== VISITOR DEVICES ===========
                       -- user's browser
                       device.browser,
                       -- user's operating system
                       device.operatingSystem AS os,
                       -- user's type of device
                       device.deviceCategory,
                       -- =========== PROMOTION ===========
                       h.promotion,
                       h.promotionActionInfo AS pa_info,
                       -- =========== PRODUCT ===========
                       h.product,
                       -- =========== ML LABEL (DEPENDENT VARIABLE) ===========
                       made_purchase_on_future_visit
                FROM `data-to-insights.ecommerce.web_analytics`,
                UNNEST(hits) AS h
                INNER JOIN returning_visitors USING (fullvisitorid)
                WHERE date BETWEEN '{split_start_date}' AND '{split_end_date}'
                AND geoNetwork.country = 'United States'
                AND totals.newVisits = 1
            ),
            -- Step 4. get aggregated features (attributes) per visit
            visit_attributes AS (
                SELECT fullvisitorid,
                       visitId,
                       visitNumber,
                       visitStartTime,
                       quarter,
                       month,
                       day_of_month,
                       day_of_week,
                       hour,
                       minute,
                       second,
                       source,
                       medium,
                       channelGrouping,
                       hits,
                       bounces,
                       -- get the last action performed during the first visit
                       -- (this indicates where the visitor left off at the end of their visit)
                       MAX(action_type) AS last_action,
                       -- get number of promotions displayed and clicked during the first visit
                       COUNT(CASE WHEN pa_info IS NOT NULL THEN pa_info.promoIsView ELSE NULL END) AS promos_displayed,
                       COUNT(CASE WHEN pa_info IS NOT NULL THEN pa_info.promoIsClick ELSE NULL END) AS promos_clicked,
                       -- get number of products displayed and clicked during the first visit
                       COUNT(CASE WHEN pu.isImpression IS NULL THEN NULL ELSE 1 END) AS product_views,
                       COUNT(CASE WHEN pu.isClick IS NULL THEN NULL ELSE 1 END) AS product_clicks,
                       pageviews,
                       time_on_site,
                       browser,
                       os,
                       deviceCategory,
                       SUM(added_to_cart) AS added_to_cart,
                       made_purchase_on_future_visit,
                FROM first_visit_attributes
                LEFT JOIN UNNEST(promotion) as p
                LEFT JOIN UNNEST(product) as pu
                GROUP BY fullvisitorid,
                         visitId,
                         visitNumber,
                         visitStartTime,
                         quarter,
                         month,
                         day_of_month,
                         day_of_week,
                         hour,
                         minute,
                         second,
                         source,
                         medium,
                         channelGrouping,
                         hits,
                         bounces,
                         pageviews,
                         time_on_site,
                         browser,
                         os,
                         deviceCategory,
                         made_purchase_on_future_visit
            )
            SELECT *
            FROM visit_attributes
            """
    return query_str


def get_sql_query_infer(split_start_date: str, split_end_date: str) -> str:
    """Assemble query to retrieve attributes about first visits."""
    query_str = f"""
            WITH
            -- Steps 1. and 2. get attributes of the first visit
            first_visit_attributes AS (
                SELECT -- =========== GEOSPATIAL AND TEMPORAL ATTRIBUTES OF VISIT ===========
                       geoNetwork.country,
                       EXTRACT(QUARTER FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS quarter,
                       EXTRACT(MONTH FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS month,
                       EXTRACT(DAY FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS day_of_month,
                       EXTRACT(DAYOFWEEK FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS day_of_week,
                       EXTRACT(HOUR FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS hour,
                       EXTRACT(MINUTE FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS minute,
                       EXTRACT(SECOND FROM DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific')) AS second,
                       -- =========== VISIT AND VISITOR METADATA ===========
                       fullvisitorid,
                       visitId,
                       visitNumber,
                       DATETIME(TIMESTAMP(TIMESTAMP_SECONDS(visitStartTime)), 'US/Pacific') AS visitStartTime,
                       -- =========== SOURCE OF SITE TRAFFIC ===========
                       -- source of the traffic from which the visit was initiated
                       trafficSource.source,
                       -- medium of the traffic from which the visit was initiated
                       trafficSource.medium,
                       -- referring channel connected to visit
                       channelGrouping,
                       -- =========== VISITOR ACTIVITY ===========
                       -- total number of hits
                       (CASE WHEN totals.hits > 0 THEN totals.hits ELSE 0 END) AS hits,
                       -- number of bounces
                       (CASE WHEN totals.bounces > 0 THEN totals.bounces ELSE 0 END) AS bounces,
                       -- action performed during first visit
                       CAST(h.eCommerceAction.action_type AS INT64) AS action_type,
                       -- page views
                       IFNULL(totals.pageviews, 0) AS pageviews,
                       -- time on the website
                       IFNULL(totals.timeOnSite, 0) AS time_on_site,
                       -- whether add-to-cart was performed during visit
                       (CASE WHEN CAST(h.eCommerceAction.action_type AS INT64) = 3 THEN 1 ELSE 0 END) AS added_to_cart,
                       -- =========== VISITOR DEVICES ===========
                       -- user's browser
                       device.browser,
                       -- user's operating system
                       device.operatingSystem AS os,
                       -- user's type of device
                       device.deviceCategory,
                       -- =========== PROMOTION ===========
                       h.promotion,
                       h.promotionActionInfo AS pa_info,
                       -- =========== PRODUCT ===========
                       h.product
                FROM `data-to-insights.ecommerce.web_analytics`,
                UNNEST(hits) AS h
                WHERE date BETWEEN '{split_start_date}' AND '{split_end_date}'
                AND geoNetwork.country = 'United States'
                AND totals.newVisits = 1
            ),
            -- Step 3. get aggregated features (attributes) per visit
            visit_attributes AS (
                SELECT fullvisitorid,
                       visitId,
                       visitNumber,
                       visitStartTime,
                       quarter,
                       month,
                       day_of_month,
                       day_of_week,
                       hour,
                       minute,
                       second,
                       source,
                       medium,
                       channelGrouping,
                       hits,
                       bounces,
                       -- get the last action performed during the first visit
                       -- (this indicates where the visitor left off at the end of their visit)
                       MAX(action_type) AS last_action,
                       -- get number of promotions displayed and clicked during the first visit
                       COUNT(CASE WHEN pa_info IS NOT NULL THEN pa_info.promoIsView ELSE NULL END) AS promos_displayed,
                       COUNT(CASE WHEN pa_info IS NOT NULL THEN pa_info.promoIsClick ELSE NULL END) AS promos_clicked,
                       -- get number of products displayed and clicked during the first visit
                       COUNT(CASE WHEN pu.isImpression IS NULL THEN NULL ELSE 1 END) AS product_views,
                       COUNT(CASE WHEN pu.isClick IS NULL THEN NULL ELSE 1 END) AS product_clicks,
                       pageviews,
                       time_on_site,
                       browser,
                       os,
                       deviceCategory,
                       SUM(added_to_cart) AS added_to_cart
                FROM first_visit_attributes
                LEFT JOIN UNNEST(promotion) as p
                LEFT JOIN UNNEST(product) as pu
                GROUP BY fullvisitorid,
                         visitId,
                         visitNumber,
                         visitStartTime,
                         quarter,
                         month,
                         day_of_month,
                         day_of_week,
                         hour,
                         minute,
                         second,
                         source,
                         medium,
                         channelGrouping,
                         hits,
                         bounces,
                         pageviews,
                         time_on_site,
                         browser,
                         os,
                         deviceCategory
            )
            SELECT *
            FROM visit_attributes
            """
    return query_str


def run_sql_query(
    query: str,
    gcp_project_id: str,
    gcp_creds: os.PathLike,
    show_dtypes: bool = False,
    show_info: bool = False,
    show_df: bool = False,
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
    if show_df:
        with pd.option_context("display.max_columns", None):
            display(df)
    if show_dtypes:
        display(df.dtypes.rename("dtype").to_frame().transpose())
    if show_info:
        df.info()
    return df
