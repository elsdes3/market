#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Define utilities to customize Streamlit page."""

from typing import Dict

import streamlit as st

# pylint: disable=dangerous-default-value


def set_page_config(
    title: str = "Propensity and Analytics Dashboard",
    layout: str = "wide",
    page_icon: str = ":ice_cube:",
    sidebar_initial_state: str = "expanded",
    menu_items: Dict[str, str] = {
        "Get Help": "https://github.com/elsdes3/market/issues",
        "Report a bug": "https://github.com/elsdes3/market/pulls",
        "About": (
            "Visualize tracking data and factors important to predicting "
            "propensity, for first-time visitors during production period"
        ),
    },
):
    """."""
    st.set_page_config(
        page_title=title,
        layout=layout,
        page_icon=page_icon,
        initial_sidebar_state=sidebar_initial_state,
        menu_items=menu_items,
    )


def add_sidebar_logo_title():
    """."""
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(http://placekitten.com/175/175);
                background-repeat: no-repeat;
                padding-top: 100px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "Select Action";
                margin-left: 20px;
                margin-top: 5px;
                font-size: 25px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_page():
    """."""
    # Customize padding in sidebar
    st.write(
        """
        <style>div.block-container{padding-top:0rem;padding-left:0rem;
        padding-bottom:0rem;padding-right:0rem}</style>
        """,
        unsafe_allow_html=True,
    )
    # Customize width of sidebar
    st.markdown(
        """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 225px;
           max-width: 225px;
       }
       """,
        unsafe_allow_html=True,
    )
    # Customize padding in main body
    margins_css = """
        <style>
            .main > div {
                padding-left: 1.25rem;
                padding-right: 5rem;
                padding-top: 0rem;
                padding-bottom: 0rem
            }
        </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)
    # Increase font size of tab headings
    font_css = """
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
    font-size: 20px;}
    </style>
    """
    st.write(font_css, unsafe_allow_html=True)
    # Hide Altair charts actions menu
    st.markdown(
        "<style type='text/css'> details {display: none;}</style>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
        .big-font {
            font-size:18px !important;
            color:grey
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Customize download button
    st.markdown(
        """
        <style>
        div.stDownloadButton > button:first-child {background-color:#218a36;
        color:#ffffff;border-color:#218a36;font-size:20px;height:2em;width:
        12em;}
        div.stDownloadButton > button:hover {background-color:#167629;
        color:#ffffff;border-color:#167629;font-size:20px;height:2em;width:
        12em;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    # add sidebar logo
    add_sidebar_logo_title()


def print_custom_text(
    text: str, font_size: int = 20, font_color: str = "grey"
) -> None:
    """Print text to screen using custom font."""
    # # ORIGINAL
    # st.markdown(
    #     f"<p class='big-font'>{text}</p>",
    #     unsafe_allow_html=True,
    # )
    # UPDATED
    st.markdown(
        f"<p style='color:{font_color};font-size:"
        f"{font_size}px;'>{text}</p>",
        unsafe_allow_html=True,
    )
