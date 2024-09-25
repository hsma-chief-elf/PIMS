import streamlit as st

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

with col_right:
    new_burst = st.text_area(
        "What do you want to tell us? (Max 200 characters)",
        max_chars=200)

