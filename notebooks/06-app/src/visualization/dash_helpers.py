#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to create dashboard plots."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments

from typing import Dict, List, Union

import altair as alt
import pandas as pd


def plot_statistic_bar_chart_combo(
    data: pd.DataFrame,
    yvar: str,
    color_by_col: str,
    marker_size: int,
    marker_colors: List[str],
    marker_values: List[Union[str, bool]],
    x_axis_sort: List[str],
    ptitle: str,
    axis_label_fontsize: int = 16,
    title_fontsize: int = 18,
    title_fontweight: str = "bold",
    ptitle_vertical_offset: int = 5,
    fig_size_bars: Dict[str, int] = dict(width=400, height=300),
    fig_size_lines: Dict[str, int] = dict(width=400, height=300),
) -> alt.Chart:
    """Plot summary statistic and its month-over-month change."""
    tooltip_bars = [
        alt.Tooltip("month", title="Month"),
        alt.Tooltip("audience_strategy", title="Audience Strategy"),
        alt.Tooltip(yvar, title=yvar.replace("_", " ").title(), format=",.2f"),
    ]
    tooltip_line = [
        alt.Tooltip("month", title="Month"),
        alt.Tooltip("audience_strategy", title="Audience Strategy"),
        alt.Tooltip(
            f"{yvar}_pct_change", title="Monthly Change (%)", format=",.2f"
        ),
        alt.Tooltip(f"{yvar}_pct_change_gt_0", title="Observed Growth"),
    ]
    bars = (
        alt.Chart(data, title=ptitle)
        .mark_bar()
        .properties(**fig_size_bars)
        .encode(
            x=alt.X(
                "month:O",
                sort=x_axis_sort,
                title=None,
                axis=alt.Axis(labelAngle=0, labels=False),
            ),
            y=alt.Y(f"{yvar}:Q", title=None),
            color=alt.Color(
                color_by_col,
                scale=alt.Scale(
                    domain=["Train+Val", "Test", "Infer"],
                    range=["lightgrey", "grey", "red"],
                ),
                title=None,
            ),
            tooltip=tooltip_bars,
        )
    )
    points = (
        alt.Chart(data)
        .mark_point(filled=True, size=marker_size, opacity=1)
        .encode(
            x=alt.X(
                "month:O",
                sort=x_axis_sort,
                title=None,
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y(f"{yvar}_pct_change:Q", title=None),
            color=alt.Color(
                f"{yvar}_pct_change_gt_0:N",
                scale=alt.Scale(
                    domain=marker_values,
                    range=marker_colors,
                ),
                title="Growth",
            ),
            tooltip=tooltip_line,
        )
    )
    line = (
        alt.Chart(data, title="Month-over-Month Difference (%)")
        .mark_line(color="#darkgrey")
        .encode(
            x=alt.X(
                "month:O",
                sort=x_axis_sort,
                title=None,
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y(f"{yvar}_pct_change:Q", title=None),
            tooltip=tooltip_line,
        )
        .encode(y=alt.Y(f"{yvar}_pct_change:Q", title=None))
    ).properties(**fig_size_lines)
    zero_line = (
        alt.Chart(pd.DataFrame({yvar: [0]}))
        .mark_rule(color="#969696")
        .encode(y=yvar)
    )
    chart = (
        alt.vconcat(bars, alt.layer(zero_line, line, points))
        .resolve_scale(y="independent", color="independent")
        .configure_view(strokeWidth=0)
        .configure(concat=alt.CompositionConfig(spacing=5))
        .configure_axisY(ticks=False)
        .configure_axisX(labelAlign="center", ticks=False)
        .configure_axis(
            labelFontSize=axis_label_fontsize,
            titleFontWeight="normal",
            grid=True,
            gridOpacity=0.5,
        )
        .configure_title(
            anchor="middle",
            offset=ptitle_vertical_offset,
            fontSize=title_fontsize,
            fontWeight=title_fontweight,
        )
        .configure_legend(labelFontSize=axis_label_fontsize)
    )
    return chart


def plot_feature_importances(
    data: pd.DataFrame,
    y_label_width: int,
    axis_label_fontsize: int,
    tooltip: List[alt.Tooltip],
    interactive: bool = False,
    bar_color: str = "red",
    show_x_ticks: bool = True,
    fig_size: Dict[str, int] = dict(width=400, height=300),
) -> alt.Chart:
    """Plot feature importances for ML model, by audience group."""
    maudiences = data["maudience"].unique().tolist()
    if not interactive:
        data = data.query(f"maudience == '{maudiences[0]}'")
    chart = (
        alt.Chart(data)
        .mark_bar(color=bar_color)
        .encode(
            x=alt.X("value:Q", title=None),
            y=alt.Y("stat:N", title=None).sort("-x"),
            tooltip=tooltip,
        )
    )
    if interactive:
        genre_dropdown = alt.binding_select(
            options=maudiences, name="Audience Group"
        )
        genre_select = alt.selection_point(
            fields=["maudience"], bind=genre_dropdown
        )
        chart = chart.add_params(genre_select).transform_filter(genre_select)
    chart = (
        chart.properties(**fig_size)
        .configure_view(strokeWidth=0)
        .configure_axisY(ticks=False, labels=False)
        .configure_axisY(labelLimit=y_label_width, ticks=False)
        .configure_axisX(labelAlign="center", ticks=show_x_ticks)
        .configure_axis(
            labelFontSize=axis_label_fontsize,
            titleFontWeight="normal",
            grid=True,
            gridOpacity=0.5,
        )
    )
    return chart


def plot_time_dependent_scatter_chart(
    data: pd.DataFrame,
    yvar: str,
    line_thickness: float,
    color_by_col: str,
    ptitle_str: str,
    axis_title_fontsize: int,
    axis_label_fontsize: int,
    axis_label_angle: int,
    axis_tick_label_color: str,
    marker_order: List[str],
    marker_colors: List[str],
    marker_size: int,
    show_title: Union[bool, str],
    show_legend: bool,
    legend_params: Dict[str, Dict[str, Union[str, int]]],
    tooltip: List[alt.Tooltip],
    ci_level: int = 0.95,
    fig_size: Dict[str, int] = dict(width=800, height=150),
) -> alt.Chart:
    """Create scatter chart daily aggregated data."""
    # get title
    ptitle = (
        alt.TitleParams(
            ptitle_str,
            anchor="start",
            fontSize=axis_title_fontsize,
            fontWeight="normal",
        )
        if show_title
        else ""
    )
    # plot scatter chart
    chart = (
        alt.Chart(data, title=ptitle)
        .mark_circle(
            strokeWidth=line_thickness,
            opacity=1,
            stroke="white",
            size=marker_size,
        )
        .encode(
            x=alt.X(
                "date:T",
                title=None,
                axis=alt.Axis(
                    labelAngle=axis_label_angle,
                    labelFontSize=axis_label_fontsize,
                    ticks=False,
                    domain=True,
                ),
            ),
            y=alt.Y(
                f"{yvar}:Q",
                title=None,
                axis=alt.Axis(
                    labelFontSize=axis_label_fontsize,
                    ticks=False,
                    domain=False,
                ),
            ),
            color=alt.Color(
                f"{color_by_col}:N",
                scale=alt.Scale(
                    domain=marker_order,
                    range=marker_colors,
                ),
                title=None,
                legend=(
                    alt.Legend(
                        labelFontSize=axis_label_fontsize,
                        **legend_params["scatter"],
                    )
                    if show_legend
                    else None
                ),
            ),
            tooltip=tooltip,
        )
    )
    # shading for holiday season
    cutoffs = (
        pd.DataFrame(
            {
                "start": ["2016-11-01"],
                "stop": ["2016-12-25"],
            },
            index=["Holiday season"],
        )
        .reset_index()
        .assign(start=lambda df: pd.to_datetime(df["start"], utc=False))
        .assign(stop=lambda df: pd.to_datetime(df["stop"], utc=False))
        .astype({"index": pd.StringDtype()})
    )
    areas = (
        alt.Chart(cutoffs)
        .mark_rect(opacity=0.075)
        .encode(
            x="start",
            x2="stop:Q",
            y=alt.value(0),
            y2=alt.value(fig_size["height"]),
            color=alt.Color(
                "index:N",
                title=None,
                scale=alt.Scale(domain=["Holiday season"], range=["red"]),
                legend=alt.Legend(
                    labelFontSize=axis_label_fontsize, **legend_params["area"]
                )
                if show_legend
                else None,
            ),
        )
    )
    # plot standard deviation bounds
    ci_int = {0.997: 3, 0.95: 2, 0.66: 1}
    upper, lower = [
        data[yvar].mean() + (ci_int[ci_level] * data[yvar].std()),
        data[yvar].mean() - (ci_int[ci_level] * data[yvar].std()),
    ]
    ci_label = f"{ci_level*100}% c.i. (dev.)"
    upper_line, lower_line = [
        (
            alt.Chart(pd.DataFrame({yvar: [line_val]}).assign(color=ci_label))
            .mark_rule(
                color="black", strokeWidth=2, opacity=0.6, strokeDash=[8, 8]
            )
            .encode(
                y=alt.Y(f"{yvar}:Q", title=None),
                color=alt.Color(
                    "color:N",
                    title=None,
                    scale=alt.Scale(domain=[ci_label], range=["black"]),
                    legend=alt.Legend(
                        labelFontSize=axis_label_fontsize,
                        **legend_params["line"],
                    )
                    if k == 0 and show_legend
                    else None,
                ),
            )
        )
        for k, line_val in enumerate([lower, upper])
    ]
    # plot combined chart
    chart = (
        alt.layer(chart, upper_line, lower_line, areas)
        .properties(**fig_size)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=False, labelColor=axis_tick_label_color)
        .resolve_scale(color="independent")
        .interactive()
    )
    return chart


def plot_stacked_bar_chart(
    data: pd.DataFrame,
    xvar: str,
    yvar: str,
    color_by_col: str,
    colors: Dict[str, str],
    show_title: Union[bool, str],
    show_legend: bool,
    ptitle_str: str,
    tooltip: List[alt.Tooltip],
    x_label_height: int = 400,
    axis_label_fontsize: int = 16,
    title_fontsize: int = 18,
    title_fontweight: str = "normal",
    x_tick_label_angle: int = -25,
    fig_size: Dict[str, int] = dict(width=525, height=300),
) -> alt.Chart:
    """Plot stacked bar chart."""
    ptitle = (
        alt.TitleParams(
            ptitle_str,
            anchor="start",
            fontSize=title_fontsize,
        )
        if show_title
        else ""
    )
    chart = (
        alt.Chart(data, title=ptitle)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{xvar}:N",
                sort=None,
                title=None,
                axis=alt.Axis(labelAngle=x_tick_label_angle, ticks=False),
            ),
            y=alt.Y(
                f"{yvar}:Q",
                title="Rate (%)",
                axis=alt.Axis(domain=False, ticks=False),
            ),
            color=alt.Color(
                f"{color_by_col}:N",
                title=None,
                scale=alt.Scale(
                    domain=list(colors), range=list(colors.values())
                ),
                legend=(
                    alt.Legend(direction="vertical") if show_legend else None
                ),
            ),
            tooltip=tooltip,
        )
    )
    chart = (
        chart.properties(**fig_size)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelFontSize=axis_label_fontsize,
            titleFontSize=axis_label_fontsize,
            titleFontWeight="normal",
            grid=False,
        )
        .configure_title(
            anchor="middle",
            fontSize=title_fontsize,
            fontWeight=title_fontweight,
        )
        .configure_axisX(labelLimit=x_label_height)
        .configure_legend(labelFontSize=axis_label_fontsize)
    )
    return chart
