import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.title("Welcome to PIMS - The PenCHORD Impact Store")

col_left, col_right = st.columns([0.3, 0.7])

with col_left:
    new_name = st.text_input(
        "What's your name?"
    )

    new_area = st.selectbox(
        "Which area of work?",
        ["HSMA", "Core PenCHORD"]
    )

    col_month, col_year = st.columns(2)

    with col_month:
        new_month = st.selectbox(
            "Month",
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
             "Sep", "Oct", "Nov", "Dec"],
             index = (datetime.today().month - 1)
        )

    with col_year:
        new_year = st.number_input(
            "Year",
            min_value=2010,
            max_value=2099,
            value=(datetime.today().year)
        )

with col_right:
    new_burst = st.text_area(
        "What do you want to tell us? (Max 200 characters)",
        max_chars=200)

new_link = st.text_input(
    "Is there a link where we can find out more?"
)

