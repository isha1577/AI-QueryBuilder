import streamlit as st

st.set_page_config(page_title="Abner Chatboard")
# from module.authentication import authenticator
import pandas as pd
import plotly.express as px
from module.connection import insert_or_increment_question, fetch_fav, update_fav, fetch_data, get_faq_id_by_question
from module.chatbot import get_gemini_response, prompt

import streamlit_authenticator as stauth

names = ['Admin', 'LeadRo']
usernames = ['admin', 'leadRo']
passwords = ['password123', 'root456']
hashed_passwords = stauth.Hasher(passwords).generate()
cache = st.session_state.get('cache', False)
def process_question_and_display(question, prompt, cache):
    try:
        del st.session_state['selected_question']

        generated_sql = get_gemini_response(question.strip(), prompt)
        print(generated_sql)

        # Step 2: Fetch data
        df = fetch_data(generated_sql)
        st.success("Data generated! Go to the chatmore page to view <-")
        st.switch_page("pages/Chat More.py")
        # Step 3: Plotting based on available columns
        if 'urgency' in df.columns:
            fig = px.bar(df['urgency'].value_counts().reset_index(), x='count', y='urgency')
            st.plotly_chart(fig)

        if 'month' in df.columns and 'lead_count' in df.columns:
            df['month'] = pd.to_datetime(df['month'])
            fig = px.line(df.sort_values('month'), x='month', y='lead_count')
            st.plotly_chart(fig)

        if 'contact_designation' in df.columns:
            fig = px.bar(df.sort_values('lead_count'), x='lead_count', y='contact_designation', orientation='h')
            st.plotly_chart(fig)

        if 'month' in df.columns and 'total_revenue' in df.columns:
            fig = px.bar(df.sort_values('month'), x='month', y='total_revenue')
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        print(f"error message = {e}")
        st.error(f"I lost my way")



authenticator = stauth.Authenticate(
    credentials={
        "usernames": {
            usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
            usernames[1]: {"name": names[1], "password": hashed_passwords[1]},
        }
    },
    cookie_name='some_cookie_name',
    key='some_signature_key',
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login('Login', 'main')

# Store the authentication status in session_state
st.session_state["authentication_status"] = authentication_status

# Handle different authentication outcomes
if authentication_status is False:
    st.error("❌ Username/password is incorrect.")

elif authentication_status is None:
    st.warning("🔐 Please enter your username and password.")

elif authentication_status is True:
    small_button = st.markdown("""
        <style>
            .small-button {
                font-size: 12px;
                padding: 5px 10px;
                background-color: #f63366;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.success(f"Welcome {name}!")
    st.title("🧠 What’s on your mind?")

    question = st.text_input(label="input", label_visibility="hidden", placeholder="Ask a question", key="input")
    col1, col2 = st.columns([1, 0.1])
    faq_id = ""

    with col1:
        submit = st.button("Submit")
    with col2:
        fav = st.button("❤️", help="Add to favorites")

    if submit and question.strip():

        faq_id = insert_or_increment_question(question.strip())
        process_question_and_display(question.strip(), prompt, False)

    if fav and question.strip():
        if not faq_id:
            faq_id = get_faq_id_by_question(question.strip())
        update_fav(faq_id, True)
        st.success("Added to favorites!")
        st.rerun()

    # 1. Initialize a session_state variable to store which question is selected
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = None

    with st.sidebar:
        st.header("⭐ Favorite Questions")
        for faq in [f for f in fetch_fav() if f["favorite"]]:
            with st.expander(faq['questions'][:150]):
                col1, col2 = st.columns([1, 0.7])
                with col2:
                    if st.button("❌ Remove Favorite", key=f"remove_fav_{faq['id']}"):
                        update_fav(faq["id"], False)
                        st.rerun()
                with col1:
                    if st.button("💬 Answer", key=f"answer_fav_{faq['id']}"):
                        st.session_state.selected_question = faq['questions']

        st.divider()

        st.header("📈 Frequently Asked")
        for faq in [f for f in fetch_fav() if not f["favorite"]][:15]:
            with st.expander(faq['questions'][:150]):
                col1, col2 = st.columns([1, 0.7])
                with col2:
                    if st.button("⭐ Add to Favorite", key=f"add_fav_{faq['id']}"):
                        update_fav(faq["id"], True)
                        st.rerun()
                with col1:
                    if st.button("💬 Answer", key=f"answer_fav_freq_{faq['id']}"):
                        st.session_state.selected_question = faq['questions']

    # If user clicks any Answer button, process it here!
    if st.session_state.selected_question:
        st.write(f"Q. {st.session_state.selected_question}")
        process_question_and_display(st.session_state.selected_question, prompt, True)
        if st.button("Clear", help="Clear Cache"):
            del st.session_state['selected_question']

        authenticator.logout('Logout', 'sidebar')
