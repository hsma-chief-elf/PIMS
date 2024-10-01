import streamlit as st
from datetime import datetime
from supabase import create_client, Client
from wordcloud import WordCloud, STOPWORDS
import string
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# https://docs.streamlit.io/develop/tutorials/databases/supabase
# Need to copy app secrets to the cloud on deployment - see instructions in link
# above

stopwords = set(STOPWORDS)

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def run_query():
    return supabase.table("pims_table").select("*").execute()

st.title("Welcome to PIMS - The PenCHORD Impact Store")

col_left, col_mid, col_right = st.columns([0.2, 0.4, 0.4])

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

with col_mid:
    new_blurb = st.text_area(
        "What do you want to tell us? (Max 200 characters)",
        max_chars=200)
    
    new_link = st.text_input(
    "Is there a link where we can find out more?"
    )

with col_right:
    rows = run_query()

    all_blurb_text = ""

    for row in rows.data:
        all_blurb_text += row['blurb']
        all_blurb_text += " "

    tokens = all_blurb_text.split()

    punctuation_mapping_table = str.maketrans('', '', string.punctuation)

    tokens_stripped_of_punctuation = [
        token.translate(punctuation_mapping_table) for token in tokens
        ]
    
    lower_tokens = [token.lower() for token in tokens_stripped_of_punctuation]

    joined_string = (" ").join(lower_tokens)

    wordcloud = WordCloud(width=1800,
                          height=1800,
                          background_color='white',
                          stopwords=stopwords,
                          min_font_size=20).generate(joined_string)
    
    plt.figure(figsize=(7,2.5))
    plt.axis("off")
    plt.imshow(wordcloud)
    plt.savefig("pims_wordcloud.png")
    st.image("pims_wordcloud.png")

button_submit_story = st.button("Submit Story")

if button_submit_story:
    rows = run_query()

    id_of_latest_entry = rows.data[(len(rows.data) - 1)]['id']
    
    response = (
        supabase.table("pims_table").insert({
            "id":(id_of_latest_entry+1),
            "name":new_name,
            "area":new_area,
            "month":new_month,
            "year":new_year,
            "blurb":new_blurb,
            "link":new_link
        }).execute()
    )

rows = run_query()

tab_blurbs, tab_placeholder = st.tabs(["What's been happening?",
                                       "Placeholder"])

with tab_blurbs:
    for i in range(len(rows.data)-1, -1, -1):
        st.write(f"{rows.data[i]['name']} *{rows.data[i]['area']}* ",
                f"({rows.data[i]['month']} {rows.data[i]['year']}) :")
        if rows.data[i]['area'] == "HSMA":
            st.info((rows.data[i]['blurb'] + '\n\n' + rows.data[i]['link']))
        else:
            st.success((rows.data[i]['blurb'] + '\n\n' + rows.data[i]['link']))
  
## Zero out text inputs after submission (after button push)
