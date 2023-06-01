#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to perform statistical analysis."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument


import numpy as np
from statsmodels.stats import gof, power


def calc_chisquared_sample_size(
    baseline_conversion_rate_percentage: np.float64,
    expected_uplift_percentage: np.float64,
    power_percentage: np.float64 = 80,
    confidence_level_percentage: np.float64 = 95,
) -> np.float64:
    """Estimates the minimum sample size when the KPI is conversion rate.

    Estimated sample size using the Chi-squared test of proportions is the
      minimum required for either a Test or a Control group in an A/B test.

    Args:
      baseline_conversion_rate_percentage: Baseline conversion rate as a
      percentage.
      expected_uplift_percentage: Expected uplift of the media experiment on
      the baseline conversion rate as a percentage.
      power_percentage: Statistical power of the Chi-squared test as a percent
      confidence_level_percentage: Statistical confidence level of the
      Chi-squared test as a percentage.

    Returns:
      sample_size: Estimated minimum sample size required for either a Test or
        a Control group.
    """
    null_probability = baseline_conversion_rate_percentage / 100
    alternative_probability = (
        null_probability * (100 + expected_uplift_percentage) / 100
    )
    alpha_proportion = (100 - confidence_level_percentage) / 100
    power_proportion = power_percentage / 100

    effect_size = gof.chisquare_effectsize(
        probs0=[null_probability, 1 - null_probability],
        probs1=[alternative_probability, 1 - alternative_probability],
        correction=None,
        cohen=True,
        axis=0,
    )
    power_test = power.GofChisquarePower()
    sample_size = power_test.solve_power(
        effect_size=effect_size,
        nobs=None,
        alpha=alpha_proportion,
        power=power_proportion,
        n_bins=2,
    )

    return np.ceil(sample_size)
