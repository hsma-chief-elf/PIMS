import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# https://docs.streamlit.io/develop/tutorials/databases/supabase
# Need to copy app secrets to the cloud on deployment - see instructions in link
# above

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

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

#response = (
#    supabase.table("pims_table").insert({
#        "name":"Sammi Rosser",
#        "area":"HSMA",
#        "month":"Aug",
#        "year":"2023",
#        "blurb":"This is another test",
#        "link":"https://www.youtube.com/@hsma"
#    }).execute()
#)

@st.cache_resource()
def run_query():
    return supabase.table("pims_table").select("*").execute()

rows = run_query()

for row in rows.data:
    st.write(f"{row['name']} *{row['area']}* ({row['month']} {row['year']})")
    if row['area'] == "HSMA":
        st.info((row['blurb'] + '\n\n' + row['link']))
    else:
        st.success((row['blurb'] + '\n\n' + row['link']))

