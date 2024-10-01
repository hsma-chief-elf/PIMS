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

col_left, col_mid, col_right = st.columns([0.3, 0.3, 0.4])

with col_left:
    st.write("Use this form to tell us about anything cool you've done or are",
             "doing.  Has your work made an impact?  Have you started working ",
             "on something interesting?  Have you created something useful? ",
             "Keep it concise and easy to read for a non-expert.  Only change ",
             "date if it's an older story.")

    with st.form("blurb_form", clear_on_submit=True):
        col_form_left, col_form_right = st.columns([0.5, 0.5])

        with col_form_left:
            new_name = st.text_input(
                "What's your name?"
            )

            new_month = st.selectbox(
                "Month",
                ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                "Sep", "Oct", "Nov", "Dec"],
                index = (datetime.today().month - 1)
            )

        with col_form_right:
            new_area = st.selectbox(
                "Which area of work?",
                ["HSMA", "Core PenCHORD"]
            )

            new_year = st.number_input(
                "Year",
                min_value=2010,
                max_value=2099,
                value=(datetime.today().year)
            )

        new_blurb = st.text_area(
            "What do you want to tell us? (Max 280 characters)",
            max_chars=280)
        
        new_link = st.text_input(
        "Is there a link where we can find out more?"
        )

        blurb_submitted = st.form_submit_button("Submit Story")
        if blurb_submitted:
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

with col_mid:
    st.write("Here's a word cloud of the most common words coming up across ",
             "our blurbs.  Stopwords are excluded - these are common words ",
             "like 'the', 'and' etc.  The word cloud will automatically ",
             "update as more blurbs are added!  Can you see common themes ",
             "emerging?")

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
                          colormap="winter",
                          stopwords=stopwords,
                          min_font_size=8).generate(joined_string)
    
    plt.figure(figsize=(7,6.55))
    plt.axis("off")
    plt.imshow(wordcloud)
    plt.savefig("pims_wordcloud.png")
    st.image("pims_wordcloud.png")

rows = run_query()

with col_right:
    tab_blurbs, tab_placeholder = st.tabs(["What's been happening?",
                                        "Placeholder"])
    with tab_blurbs:
        with st.container(height=600):
            for i in range(len(rows.data)-1, -1, -1):
                st.write(f"{rows.data[i]['name']} *{rows.data[i]['area']}* ",
                        f"({rows.data[i]['month']} {rows.data[i]['year']}) :")
                if rows.data[i]['area'] == "HSMA":
                    st.info((rows.data[i]['blurb'] + '\n\n' + rows.data[i]['link']))
                else:
                    st.success((rows.data[i]['blurb'] + '\n\n' + rows.data[i]['link']))
  
## Add functionality for spacy to auto visualise named entities (maybe
# organisations and names?) on whole text (all blurbs collated together)

# Add feedback / quotes functionality (output and input?)

# Add icons to blurbs (maybe auto select icons based on text detected?)

