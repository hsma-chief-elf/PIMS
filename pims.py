import streamlit as st

st.title("Welcome to PIMS - The PenCHORD Impact Store")

new_name = st.text_input(
    "What's your name?"
)

new_area = st.selectbox(
    "Which area of work?",
    ["HSMA", "Core PenCHORD"]
)

new_burst = st.text_area(
    "What do you want to tell us? (Max 200 characters)",
    max_chars=200)

