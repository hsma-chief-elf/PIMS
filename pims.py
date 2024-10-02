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
punctuation_mapping_table = str.maketrans('', '', string.punctuation)

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def run_query_main():
    return supabase.table("pims_table").select("*").execute()

def run_query_quotes():
    return supabase.table("pims_quotes_table").select("*").execute()

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
    tab_wc_impact, tab_wc_quotes = st.tabs([
        "Impact Word Cloud",
        "Quote Word Cloud"
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

rows = run_query_main()
rows_quotes = run_query_quotes()

with col_right:
    tab_blurbs, tab_quotes = st.tabs(["What's been happening?",
                                      "Quotes from partners"])
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



# FUTURE WORK  
## Add functionality for spacy to auto visualise named entities (maybe
# organisations and names?) on whole text (all blurbs collated together) / word
# clouds on organisations etc
# See https://discuss.streamlit.io/t/how-to-install-language-model-for-spacy-in-requirements-yml/30853/5

# Add icons to blurbs (maybe auto select icons based on text detected?)

# Add theming (eg forced dark mode, grey gradient background etc)

# Add logo / team photo / other graphics

# Add organisation?

# Add comments

# Add initial data

# Add open, applied, impactful about penchord

