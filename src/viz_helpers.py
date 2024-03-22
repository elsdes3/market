#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define helper utilities to create plots."""

# pylint: disable=invalid-name,dangerous-default-value
# pylint: disable=too-many-locals,unused-argument,too-many-arguments


from typing import Any, Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import ticker


def customize_splines(ax: plt.axis, color: str = "dimgrey") -> plt.axis:
    """Customize axes in matplotlib plots."""
    ax.spines["left"].set_edgecolor(color)
    ax.spines["left"].set_linewidth(1)
    ax.spines["bottom"].set_edgecolor(color)
    ax.spines["bottom"].set_linewidth(1)
    ax.spines["top"].set_linewidth(0)
    ax.spines["right"].set_linewidth(0)
    return ax


def customize_axis(
    ax: plt.axis,
    show_grid: bool = False,
    color: str = "dimgrey",
    top_right_color: str = "whitesmoke",
    linewidth: float = 1.5,
    grid_thickness: float = 0.75,
    grid_opacity: float = 0.5,
    grid_axis: str = "both",
    line_color: str = "dimgrey",
    show_top_right: bool = False,
) -> None:
    """Customize matplotlib axis properties."""
    ax.spines["left"].set_edgecolor(color)
    ax.spines["left"].set_linewidth(linewidth)
    ax.spines["bottom"].set_edgecolor(color)
    ax.spines["bottom"].set_linewidth(linewidth)
    if show_top_right:
        ax.spines["top"].set_edgecolor(top_right_color)
        ax.spines["top"].set_linewidth(linewidth)
        ax.spines["right"].set_edgecolor(top_right_color)
        ax.spines["right"].set_linewidth(linewidth)
    else:
        ax.spines["top"].set_linewidth(0)
        ax.spines["right"].set_linewidth(0)
    if show_grid:
        # ax.grid(which="both", axis="both", color="gainsboro", zorder=3)
        ax.grid(
            which="major",
            axis=grid_axis,
            linewidth=grid_thickness,
            color=line_color,
            alpha=grid_opacity,
            zorder=3,
        )


def customize_plot(
    ax: plt.axis,
    legend_params: Dict[str, Any],
    ptitle: str,
    x_tick_angle: float = 37.5,
    axis_tick_label_fontsize: int = 12,
    grid_thickness: float = 0.75,
    grid_opacity: float = 0.5,
    line_color: str = "dimgrey",
    show_grid: bool = True,
    show_legend: bool = True,
) -> None:
    """Customize matplotlib plot."""
    ax.yaxis.set_tick_params(labelsize=axis_tick_label_fontsize)
    ax.xaxis.set_tick_params(
        labelsize=axis_tick_label_fontsize, rotation=x_tick_angle
    )
    for tick in ax.xaxis.get_majorticklabels():
        tick.set_horizontalalignment("right")
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.tick_params(
        axis="both",
        which="both",
        length=0,
        bottom=False,
        top=False,
        left=False,
        colors=line_color,
    )
    ax.set_title(ptitle, fontweight="bold", loc="left")
    ax = customize_splines(ax, color=line_color)
    if show_grid:
        ax.grid(
            which="major",
            axis="y",
            linewidth=grid_thickness,
            color=line_color,
            alpha=grid_opacity,
            zorder=0,
        )
    if show_legend:
        leg = ax.legend(**legend_params)
        for text in leg.get_texts():
            plt.setp(text, color=line_color)
    else:
        ax.legend([], frameon=False)


def increase_ticklabel_fontsize(
    ax,
    fontsize: int = 12,
    xtick_locations: Union[List[int], None] = None,
    ytick_locations: Union[List[int], None] = None,
):
    """Increase fontsize of matplotlib axis tick labels."""
    if xtick_locations:
        ax.xaxis.set_major_locator(ticker.FixedLocator(xtick_locations))
    if ytick_locations:
        ax.yaxis.set_major_locator(ticker.FixedLocator(ytick_locations))
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=fontsize)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=fontsize)
    return ax


def customize_tick_props(
    ax,
    minor_len: int,
    major_len: int,
    tick_thickness: int = 1,
    color: str = "grey",
):
    """Customize matplotlib axis tick properties."""
    ax.tick_params(
        size=minor_len,
        which="minor",
        width=tick_thickness,
        color=color,
    )
    ax.tick_params(
        size=major_len,
        which="major",
        width=tick_thickness,
        color=color,
    )
    return ax


def plot_multi_line_threshold_chart(
    data: pd.DataFrame,
    ptitle_str: str,
    xlabel: str,
    ylabel: str,
    title_fontsize: int = 12,
    axis_label_fontsize: int = 12,
    figsize: Tuple[int] = (8, 4),
) -> None:
    """Plot separate lines from multiple columns of DataFrame."""
    _, ax = plt.subplots(figsize=figsize)
    ax.axvline(
        x=0.5, linewidth=1.25, linestyle="--", c="k", label="default (t=0.5)"
    )
    _ = sns.lineplot(data, ax=ax)
    ax.legend(ncol=1, bbox_to_anchor=(1, 1), loc="upper left", frameon=False)
    customize_axis(ax, True)
    ax.set_title(
        ptitle_str, loc="left", fontweight="bold", fontsize=title_fontsize
    )
    ax.set_xlabel(xlabel, fontsize=axis_label_fontsize)
    ax.set_ylabel(ylabel, fontsize=axis_label_fontsize)
    _ = customize_tick_props(ax, 4, 6, 1.25, "grey")


def plot_histogram(
    data: pd.DataFrame,
    ax,
    xvar: str,
    color_by_col: str,
    xlabel: Union[str, None],
    ylabel: Union[str, None],
    ptitle: str,
    axis_label_fontsize: int = 12,
    num_bins: int = 40,
    bin_edgecolor: str = "grey",
    bin_transparency: float = 0.2,
    set_xlog: bool = False,
    set_ylog: bool = True,
    legend_params: Dict[str, Any] = dict(
        loc="best",
        frameon=False,
        handletextpad=0.35,
        title="Return Purchasers",
    ),
    fig_size: Tuple[int] = (8, 6),
) -> None:
    """Plot histogram using seaborn."""
    if not ax:
        _, ax = plt.subplots(figsize=fig_size)
    ax = sns.histplot(
        data=data,
        x=xvar,
        hue=color_by_col,
        bins=num_bins,
        alpha=bin_transparency,
        ax=ax,
        edgecolor=bin_edgecolor,
        legend=True if legend_params else False,
    )
    if set_ylog:
        ax.set(yscale="log")
    if set_xlog:
        ax.set(xscale="log")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_label_fontsize)
    else:
        ax.set_xlabel(None)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=axis_label_fontsize)
    else:
        ax.set_ylabel(None)
    ax.set_title(ptitle, fontsize=axis_label_fontsize, loc="left")
    if legend_params:
        sns.move_legend(ax, **legend_params)
    customize_axis(ax)


def plot_boxplot(
    data: pd.DataFrame,
    ax,
    xvar: str,
    ylabel: Union[str, None],
    color_by_col: str,
    ptitle: str,
    show_xticklabels: bool = True,
    y_scale: str = "log",
    box_width: float = 0.8,
    label_color_palette: Dict[Any, str] = {True: "red", False: "lightgrey"},
    color_properties: Dict[str, str] = {
        "boxprops": {"edgecolor": "grey"},
        "flierprops": {"color": "none"},
        "medianprops": {"color": "grey"},
        "whiskerprops": {"color": "grey"},
        "capprops": {"color": "grey"},
    },
    median_annotation_props: Dict[str, Any] = dict(
        facecolor="#445A64", edgecolor="white", linewidth=1.25
    ),
    axis_label_fontsize: int = 12,
    fig_size: Tuple[int] = (8, 6),
) -> None:
    """Plot a boxplot with seaborn."""
    if not ax:
        _, ax = plt.subplots(figsize=fig_size)
    ax = sns.boxplot(
        data=data,
        y=xvar,
        x=color_by_col,
        width=box_width,
        palette=label_color_palette,
        ax=ax,
        **color_properties,
    )
    ax.set(yscale=y_scale)
    ax.set_xlabel(None)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=axis_label_fontsize)
    else:
        ax.set_ylabel(None)
    ax.tick_params(
        top=False,
        bottom=False,
        left=False,
        right=False,
        labelleft=True,
        labelbottom=True,
    )
    ax.set_title(ptitle, fontsize=axis_label_fontsize, loc="left")
    ax.legend([], frameon=False)
    if not show_xticklabels:
        ax.set_xticklabels([])
    if median_annotation_props:
        lines = ax.get_lines()
        categories = ax.get_xticks()
        for cat in categories:
            y = int(lines[4 + cat * 6].get_ydata()[0])
            ax.text(
                cat,
                y,
                f"{y}",
                ha="center",
                va="center",
                fontweight="bold",
                size=12,
                color="white",
                bbox=median_annotation_props,
            )
    customize_axis(ax)


def plot_grouped_barchart(
    data: pd.DataFrame,
    ax,
    yvar: str,
    ptitle: str,
    color_by_col: str,
    label: str,
    xlabel: Union[str, None],
    x_scale: str = "log",
    set_xlog: bool = True,
    label_color_palette: Dict[Any, str] = {True: "red", False: "lightgrey"},
    legend_params: Dict[str, Any] = dict(
        loc="best",
        frameon=False,
        handletextpad=0.35,
        title="Return Purchasers",
    ),
    axis_label_fontsize: int = 12,
    fig_size: Tuple[int] = (8, 6),
) -> None:
    """."""
    if not ax:
        _, ax = plt.subplots(figsize=fig_size)
    ax = sns.barplot(
        data=data,
        y=yvar,
        x="count",
        hue=color_by_col,
        palette=label_color_palette,
        order=data.query(label)[yvar],
        hue_order=[True, False],
        ax=ax,
    )
    if set_xlog:
        ax.set(xscale=x_scale)
    ax.set_ylabel(None)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_label_fontsize)
    else:
        ax.set_xlabel(None)
    ax.tick_params(size=0)
    ax.set_title(ptitle, loc="left", fontsize=axis_label_fontsize)
    if legend_params:
        sns.move_legend(ax, **legend_params)
    else:
        ax.legend([], frameon=False)
    customize_axis(ax)
