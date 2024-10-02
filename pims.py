import streamlit as st
from datetime import datetime
from supabase import create_client, Client
from wordcloud import WordCloud, STOPWORDS
import string
import matplotlib.pyplot as plt
import spacy
import en_core_web_sm
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide")

# https://docs.streamlit.io/develop/tutorials/databases/supabase
# Need to copy app secrets to the cloud on deployment - see instructions in link
# above

stopwords = set(STOPWORDS)
punctuation_mapping_table = str.maketrans('', '', string.punctuation)

nlp = en_core_web_sm.load()

gs_conn = st.connection("gsheets", type=GSheetsConnection)

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def run_query_main():
    return supabase.table("pims_table").select("*").execute()

def run_query_quotes():
    return supabase.table("pims_quotes_table").select("*").execute()

def create_string_people_places_impact(rows):
    raw_string = ""

    for row in rows.data:
        raw_string += row['blurb']
        raw_string += " "

    doc = nlp(raw_string)

    string_people_places_impact = ""

    for ent in doc.ents:
        if (ent.label_ == "PERSON" or
            ent.label_ == "NORP" or
            ent.label_ == "FAC" or
            ent.label_ == "ORG" or
            ent.label_ == "GPE" or
            ent.label_ == "LOC"):
            underscored_string = str(ent).replace(" ", "_")
            string_people_places_impact += underscored_string
            string_people_places_impact += " "

    return string_people_places_impact

st.title("Welcome to PIMS - The PenCHORD Impact Store")

col_left, col_mid, col_right = st.columns([0.3, 0.3, 0.4])

with col_left:
    tab_blurb_form, tab_quote_form = st.tabs(["Impact Recorder",
                                              "Quote Recorder"])
    with tab_blurb_form:
        st.write(
            "Use this form to tell us about anything cool you've done or are",
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
                rows = run_query_main()

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

    with tab_quote_form:
        st.write(
            "Use this form if you want to record a quote about your ",
            "experience of being on HSMA or working with PenCHORD.  You can ",
            "also use this form to record a quote that someone else has ",
            "provided, but please ensure that you have their permission to ",
            "use.  We may use these quotes in comms materials."
        )

        with st.form("quote_form", clear_on_submit=True):
            new_quote_name = st.text_input(
                "Name of person providing quote"
            )

            new_quote_org = st.text_input(
                "Organisation of person providing quote"
            )

            new_quote_text = st.text_area(
                "The quote"
            )

            quote_submitted = st.form_submit_button("Submit Quote")
            if quote_submitted:
                rows_quotes = run_query_quotes()

                id_of_latest_entry_quotes = rows_quotes.data[
                    (len(rows_quotes.data) - 1)
                ]['id']

                response_quote = (
                    supabase.table("pims_quotes_table").insert({
                        "id":(id_of_latest_entry_quotes+1),
                        "name":new_quote_name,
                        "org":new_quote_org,
                        "quote":new_quote_text
                    }).execute()
                )

with col_mid:
    tab_wc_impact, tab_wc_quotes, tab_wc_people_places = st.tabs([
        "Impact Word Cloud",
        "Quote Word Cloud",
        "Impact People / Places Word Cloud"
    ])

    with tab_wc_impact:
        st.write(
            "Here's a word cloud of the most common words coming up across ",
            "our blurbs.  Stopwords are excluded - these are common words ",
            "like 'the', 'and' etc.  The word cloud will automatically ",
            "update as more blurbs are added!  Can you see common themes ",
            "emerging?")

        rows = run_query_main()

        all_blurb_text = ""

        for row in rows.data:
            all_blurb_text += row['blurb']
            all_blurb_text += " "

        tokens = all_blurb_text.split()

        tokens_stripped_of_punctuation = [
            token.translate(punctuation_mapping_table) for token in tokens
            ]
        
        lower_tokens = [
            token.lower() for token in tokens_stripped_of_punctuation]

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

    with tab_wc_quotes:
        st.write("This is a word cloud of the most common words in our quotes.",
                 "Stopwords are excluded - these are common words like 'the', ",
                 "'and' etc.  The word cloud will automatically update as ",
                 "more quotes are added!  Can you see common themes emerging?")
        
        rows_quotes = run_query_quotes()

        all_quotes_text = ""

        for row in rows_quotes.data:
            all_quotes_text += row['quote']
            all_quotes_text += " "

        tokens_quotes = all_quotes_text.split()

        q_tokens_stripped_of_punctuation = [
            token.translate(punctuation_mapping_table) 
            for token in tokens_quotes
        ]

        q_lower_tokens = [
            token.lower() for token in q_tokens_stripped_of_punctuation]
        
        q_joined_string = (" ").join(q_lower_tokens)

        q_wordcloud = WordCloud(width=1800,
                                height=1800,
                                background_color='white',
                                colormap="autumn",
                                stopwords=stopwords,
                                min_font_size=8).generate(q_joined_string)
        
        plt.figure(figsize=(7,6.55))
        plt.axis("off")
        plt.imshow(q_wordcloud)
        plt.savefig("quote_wordcloud.png")
        st.image("quote_wordcloud.png")

    with tab_wc_people_places:
        st.write(
            "This word cloud uses AI! We use a pre-trained machine learning ",
            "model to attempt to automatically extract people, places and ",
            "organisations from the recorded impact blurbs, and use only ",
            "these in the word cloud.  The word cloud updates automatically ",
            "as more blurbs are added!")

        rows = run_query_main()
        returned_string_pp = create_string_people_places_impact(rows)

        tokens_pp = returned_string_pp.split()

        pp_tokens_stripped = [
            token.translate(punctuation_mapping_table) for token in tokens_pp
        ]

        pp_lower_tokens = [token.lower() for token in pp_tokens_stripped]

        pp_joined_string = (" ").join(pp_lower_tokens)

        pp_wordcloud = WordCloud(width=1800,
                                 height=1800,
                                 background_color='white',
                                 colormap="seismic",
                                 stopwords=stopwords,
                                 min_font_size=8).generate(pp_joined_string)
        
        plt.figure(figsize=(7,6.55))
        plt.axis("off")
        plt.imshow(pp_wordcloud)
        plt.savefig("pp_wordcloud.png")
        st.image("pp_wordcloud.png")

rows = run_query_main()
rows_quotes = run_query_quotes()

with col_right:
    tab_blurbs, tab_quotes, tab_h_proj_reg = st.tabs(
        ["What's been happening?",
         "Quotes from partners",
         "HSMA Project Register"])
    with tab_blurbs:
        with st.container(height=600):
            for i in range(len(rows.data)-1, -1, -1):
                st.write(f"{rows.data[i]['name']} *{rows.data[i]['area']}* ",
                        f"({rows.data[i]['month']} {rows.data[i]['year']}) :")
                if rows.data[i]['area'] == "HSMA":
                    st.info(
                        (rows.data[i]['blurb'] + '\n\n' + rows.data[i]['link']))
                else:
                    st.success(
                        (rows.data[i]['blurb'] + '\n\n' + rows.data[i]['link']))
                    
    with tab_quotes:
        with st.container(height=600):
            for j in range(len(rows_quotes.data)-1, -1, -1):
                st.write(f"{rows_quotes.data[j]['name']} ",
                        f"*{rows_quotes.data[j]['org']}* said :")
                st.error(rows_quotes.data[j]['quote'])

    with tab_h_proj_reg:
        col_p_reg_left, col_p_reg_right = st.columns([0.2, 0.8])
        
        with col_p_reg_left:
            st.image("hsma_with_slogan.png")

        with col_p_reg_right:
            st.write("This lists all of the currently active projects running ",
                     "within the HSMA Programme.  Click on a project to find ",
                     "out more about it.  Projects with recent impact reports ",
                     "are also flagged."
                     )
            
        with st.container(height=490):
            hsma_proj_reg_df = gs_conn.read()

            for index, row in hsma_proj_reg_df.iterrows():
                headline = ""

                if row['Impact to Report'] == "Yes":
                    headline += ":green[This project has impact to report!]"
                    headline += "\n\n"

                headline += (
                    str(row['Project Code']) + " : " + row['Project Title'] + 
                    "\n\n" + "*" + row['Lead Org'] + "*"
                )

                with st.expander(headline):
                    st.write(f"Project Lead : {row['Lead']}")

                    if row['Impact to Report'] == "Yes":
                        st.write(
                            f":green[IMPACT UPDATE! {row['Impact / Outcomes']}]"
                        )

                    st.write(f"Methods Used : {row['Method Area(s)']}")
                    st.write(row['Additional Notes'])
                    
# FUTURE WORK  
# Need to add en_core_web_sm when deploying
# See https://discuss.streamlit.io/t/how-to-install-language-model-for-spacy-in-requirements-yml/30853/5

# Add icons to blurbs (maybe auto select icons based on text detected?)

# Add logo / team photo / other graphics

# Add organisation?

# Add comments

# Add initial data

# Add open, applied, impactful about penchord

