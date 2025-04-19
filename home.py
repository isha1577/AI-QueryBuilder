import streamlit as st
import pandas as pd
import plotly.express as px
from module.connection import insert_or_increment_question, fetch_fav, update_fav, fetch_data
from module.chatbot import get_gemini_response, prompt
from module.authentication import authenticator
st.set_page_config(page_title="Abner Dashboard", layout="centered")

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status not in st.session_state:
    st.session_state["authentication_status"] = None

if authentication_status:
    st.sidebar.success(f"Welcome {name}!")
    st.title("Abner DashPage")
    question = st.text_input(label="", placeholder="Ask a question", key="input")
    submit = st.button("Submit")
    if question:
        fav = st.button("add to fav")

        if fav:
            faq_id = insert_or_increment_question(question.strip())
            update_fav(faq_id, True)
            st.rerun()

    if (question or submit) and question.strip():
        with st.spinner("Let me think..."):
            generated_sql = get_gemini_response(question.strip(), prompt)
            st.code(generated_sql, language="sql")
            try:
                df = fetch_data(generated_sql)
                st.success("Data generated! Go to the Results page to view <-")

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
                st.error(f"❌ Error: {e}")

    with st.sidebar:
        st.header("⭐ Favorite Questions")
        for faq in [f for f in fetch_fav() if f["favorite"]]:
            with st.expander(faq['questions'][:60]):
                if st.button("❌ Remove Favorite", key=f"remove_fav_{faq['id']}"):
                    update_fav(faq["id"], False)
                    st.rerun()

        st.divider()
        st.header("📈 Frequently Asked")
        for faq in [f for f in fetch_fav() if not f["favorite"]][:10]:
            with st.expander(faq['questions'][:60]):
                if st.button("⭐ Add to Favorite", key=f"add_fav_{faq['id']}"):
                    update_fav(faq["id"], True)
                    st.rerun()
                    
        authenticator.logout('Logout', 'sidebar')
elif authentication_status is False:
    st.error("❌ Username/password is incorrect.")
elif authentication_status is None:
    st.warning("🔐 Please enter your username and password.")