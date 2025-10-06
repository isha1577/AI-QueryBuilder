import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import google.generativeai as genai
from module.connection import (
    insert_or_increment_question,
    update_fav,
    fetch_data,
    get_faq_id_by_question
)
from module.chatbot import get_gemini_response, admin_prompt
from logging_setup import setup_logger

logger = setup_logger()
st.set_page_config(page_title="Abner Chatboard", layout="wide")
genai.configure(api_key="AIzaSyDMhs-8j9ZblyimVkeuJpizW-KqxDa3J2Y")  # Replace with your valid API key

CACHE_FILE = "chat_cache.json"


@st.cache_resource
def load_model():
    return genai.GenerativeModel('models/gemini-2.5-flash')


def get_gemini_response(question, prompt):
    try:
        model = load_model()
        response = model.generate_content([prompt, question])
        logger.info(response.text)
        return response.text
    except Exception as e:
        logger.warning(f"Error in Gemini response: {e}")
        return "Oops!! Sorry, I lost my way."


def process_question_and_display(chat_more, prompt, cache):
    try:
        generated_sql = get_gemini_response(chat_more, prompt)
        logger.info(generated_sql)
        df = fetch_data(generated_sql)

        if df is not None and not df.empty:
            insert_or_increment_question(chat_more)
            st.success("Data generated!")
            df.to_csv("temp_df.csv", index=False)
        else:
            st.warning("No data found.")
    except Exception as e:
        logger.warning(f"Error processing question: {e}")
        st.error("I lost my way.")


def display_summary_and_graph(df):
    try:
        if len(df) > 2:
            st.write("Summary statistics:")
            st.write(df.describe())

        if len(df.columns) >= 2 and len(df) > 1:
            graph_type = st.radio("Choose a graph type:", ['Bar', 'Line', 'Scatter', 'Pie'])
            fig = None

            if graph_type == 'Pie':
                name_cols = df.select_dtypes(include='object').columns
                value_cols = df.select_dtypes(include=['int64', 'float64']).columns

                if name_cols.empty or value_cols.empty:
                    st.error("Insufficient data for pie chart.")
                else:
                    name_col = st.selectbox("Labels column:", name_cols)
                    value_col = st.selectbox("Values column:", value_cols)
                    fig = px.pie(df, names=name_col, values=value_col, title="Pie Chart")
            else:
                x_axis = st.selectbox("X Axis", df.columns)
                y_axis = st.multiselect("Y Axis", df.columns, default=[df.columns[1]])
                if x_axis and y_axis:
                    fig = getattr(px, graph_type.lower())(df, x=x_axis, y=y_axis, title=f"{graph_type} Chart")

            if fig:
                st.plotly_chart(fig)
            else:
                st.warning("Please select valid axes.")
    except Exception as e:
        logger.warning(f"Error in summary/graph section: {e}")
        st.error("Error displaying summary or graph.")


# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Load cache file ---
if os.path.exists(CACHE_FILE) and not st.session_state.chat_history:
    try:
        with open(CACHE_FILE, "r") as f:
            st.session_state.chat_history = json.load(f)
    except Exception as e:
        logger.warning(f"Error loading cache: {e}")
        st.warning("Failed to load previous chat history.")

# --- UI Styling ---
st.markdown(
    """
    <style>
    section[data-testid='stSidebar'] { width: 250px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Content ---
st.sidebar.markdown("""
Welcome to the **Abner Chatbot**! Interact with your database using simple language.

### 🔹 Step-by-Step Guide:

1. **Ask a Question**
   - e.g., *"Show top 5 products by revenue"*

2. **AI Response**
   - See data & insights.

3. **Follow-up Questions**
   - e.g., *"Average revenue?"*

**🛠️ Tip:** Be specific and data-focused.

Happy analyzing! 📊
""")

# --- Main Area Layout ---
st.title("💬 Chat with me")
col1, col3, col2 = st.columns([1, 0.1, 1])

# faq_id = ""
if "question" not in st.session_state:
    st.session_state["question"] = ""
    #
    # with left:
    #     print(f"{st.session_state['question']}")
    # with right:
    #     if st.button("", help="Add to favorites"):
    #         faq_id = get_faq_id_by_question(st.session_state['question'])
    #         update_fav(faq_id, True)
    #         print(f"{faq_id} added to favorites.")
    #         st.success("Added to favorites!")
    #         st.rerun()

chat_more = st.chat_input("Ask a follow-up question")

if chat_more:
    # store only the latest question
    st.session_state['question'] = chat_more
    st.markdown(f"Q. {st.session_state['question']}")

    process_question_and_display(st.session_state['question'], admin_prompt, False)
else:
    st.markdown(f"Q. {st.session_state['question']}")
    logger.info("Please enter a question ⭐")

try:
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w") as f:
            json.dump([], f)

    if os.path.exists("temp_df.csv"):
        df = pd.read_csv("temp_df.csv")

        if not df.empty:
            if df.shape == (1, 1):
                col_name = df.columns[0]
                for value in df[col_name]:
                    st.code(f"{col_name}  : {value}")
            else:
                st.dataframe(df)
                display_summary_and_graph(df)
        else:
            st.write("No data found.")
    else:
        st.write("Upload or generate data first.")
except Exception as e:
    logger.warning(f"Streamlit rendering error: {e}")
    st.error("Failed to display output.")
