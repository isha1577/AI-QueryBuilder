import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import google.generativeai as genai
from module.connection import (insert_or_increment_question, update_fav, fetch_data, get_faq_id_by_question)
from module.chatbot import get_gemini_response, admin_prompt
from logging_setup import setup_logger

logger = setup_logger()
st.set_page_config(page_title="Abner Chatboard", layout="wide")
genai.configure(api_key="AIzaSyD42VSIy3Ts5XJKUfD8wOWysNUPrObWnUE")  # Replace with your valid API key

CACHE_FILE = "chat_cache.json"

@st.cache_resource
def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')


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

with col1:
    faq_id = ""
    if "question" in st.session_state:
        left, right = st.columns([1, 0.1])
        with left:
            st.markdown(f"###### Q. {st.session_state['question']}")
        with right:
            if st.button("❤️", help="Add to favorites"):
                faq_id = get_faq_id_by_question(st.session_state['question'])
                update_fav(faq_id, True)
                st.success("Added to favorites!")
                st.rerun()

    toggle_state = st.toggle("New Chat")
    chat_more = st.chat_input("Ask a follow-up question")

    if toggle_state:
        if chat_more:
            process_question_and_display(chat_more, admin_prompt, False)
            st.write(f"Q. {chat_more}")
        else:
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
                    df_prompt = df.to_csv(index=False)
                    if chat_more and not toggle_state:
                        # Gemini prompt to convert to pandas code
                        prompt1 = f"""Convert the asked question to a Pandas formula using ONLY this DataFrame: {df_prompt}
                        Only return the Pandas formula.
                        Do NOT provide explanation.
                        Do NOT use ``` in the begining or ending
                        DataFrame is called df.
                        Examples:
                        Q: how many leads are cold? → A: df[df['urgency'] == 'Cold'].shape[0]
                        Q: list top 3 products → A: df.nlargest(3, 'total revenue')['product name'].tolist()
                        Q: give component names with threshold → A: df[['component name', 'threshold']].drop_duplicates()
                        Q: list down types of driver → A: df[df['component_name'].str.contains('driver', case=False, na=False)].drop_duplicates()
                        """
                        response = get_gemini_response(chat_more, prompt1)

                        try:
                            result = eval(response)
                        except Exception as e:
                            result = "Null"
                            logger.warning(f"Code execution error: {e}")

                        logger.info(result)

                        prompt2 = f"This is the question: {chat_more}, and this is the answer: {result}"
                        ai_response = get_gemini_response("write answer like talking to an business person use rupees for money values ", prompt2)

                        st.session_state.chat_history.insert(0, {"user": chat_more, "response": ai_response})

                        with open(CACHE_FILE, "w") as f:
                            json.dump(st.session_state.chat_history, f, indent=2)
            else:
                st.write("No data found.")
        else:
            st.write("Upload or generate data first.")
    except Exception as e:
        logger.warning(f"Streamlit rendering error: {e}")
        st.error("Failed to display output.")

# --- Chat History + Clear Button ---
with col2:
    if st.button("Clear"):
        st.session_state.chat_history = []
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        st.success("Conversation and cache cleared.")

    st.subheader("📝 Chat History")

    # Scrollable chat history UI
    st.markdown("""
    <style>
        .scroll-box {
            height: 850px;
            overflow-y: scroll;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 10px;
        }
        .user-msg { font-weight: bold; margin-bottom: 4px; }
        .bot-msg { margin-bottom: 16px; }
    </style>
    """, unsafe_allow_html=True)

    chat_html = '<div class="scroll-box"><p><strong>👋 HEY THERE !!</strong></p>'
    for msg in st.session_state.chat_history:
        chat_html += f'<div class="user-msg">🤓 ME: {msg["user"]}</div>'
        chat_html += f'<div class="bot-msg">🤖 BOT: {msg["response"]}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
