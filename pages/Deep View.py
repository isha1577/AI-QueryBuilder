import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
import plotly.express as px
from sqlalchemy import Nullable

from module.connection import update_fav, get_faq_id_by_question
from logging_setup import setup_logger

logger = setup_logger()
st.set_page_config(page_title="Abner Chatboard", layout="wide")
genai.configure(api_key="AIzaSyD42VSIy3Ts5XJKUfD8wOWysNUPrObWnUE")


@st.cache_resource
def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')


def get_gemini_response(question, prompt):
    try:
        model = load_model()
        response = model.generate_content([prompt[0], question])
        logger.info(response)
        return response.text
    except Exception as e:
        return f"Oops!! sorry I lost my way"


CACHE_FILE = "chat_cache.json"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Load cache if it exists
if os.path.exists(CACHE_FILE) and not st.session_state.chat_history:
    try:
        with open(CACHE_FILE, "r") as f:
            st.session_state.chat_history = json.load(f)
    except Exception as e:
        logger.warning(f"error loading cache file {e}")
        st.warning("load cache file")
st.markdown(
    """
    <style>
    section[data-testid='stSidebar'] {
        width: 100px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("""
Welcome to the **Abner Chatbot**! This application helps you interact with your database using simple language.

### 🔹 Step-by-Step Guide:

1. **Ask a Question**
   - Type a business question like:
     - *"What were the leads in March 2024?"*
     - *"Show me the top 5 products by revenue."*

2. **AI Response**
   - The app will:
     - Generate a human-readable answer,
     - Display the **data output** from your database.

3. **Ask Follow-up Questions**
   - **Don't ask outside-database questions**  
   - You can continue the conversation using follow-up questions like:
     - *"What's the total growth rate in current month?"*
     - *"Calculate the average order value."*

4. **Interact with the Graphs**
   - Change the x/y axis to the labels of your requirement
   - display the graph as per your requirement

---
### 🛠️ Pro Tip:
Want the best results? Be **specific** and **data-oriented** in your questions.


Happy analyzing! 📊✨
""")

st.title("💬Chat with me")
data_str = ""
col1, col3, col2 = st.columns([1, 0.1, 1])
with (col1):
    faq_id = ""
    if "question" in st.session_state:
        left, right = st.columns([1, 0.1])
        with left:
            st.markdown(f"###### Q.{st.session_state['question']}")
        with right:
            fav = st.button("❤️", help="Add to favorites")
        if fav and st.session_state['question']:
            faq_id = get_faq_id_by_question(st.session_state['question'])
            update_fav(faq_id, True)
            st.success("Added to favorites!")
            st.rerun()

    chat_more = st.chat_input("Ask a follow-up question")

    try:
        if not os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w") as f:
                json.dump([], f)
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                if os.path.exists("temp_df.csv"):
                    df = pd.read_csv("temp_df.csv")
                    if df.shape == (1, 1):
                        col_name = df.columns[0]
                        for idx, value in enumerate(df[col_name]):
                            st.code(f"{col_name}  : {value}")
                    elif df is not None and not df.empty:
                        st.dataframe(df)
                        if len(df) > 2:
                            st.write("Summary statistics:")  # ----new
                            st.write(df.describe())
                        data_str = df.to_markdown(index=False)
                        df_prompt = df.to_csv(index=False)
                        if chat_more:

                            prompt1 = [f"""Convert the asked question to a Pandas formula using ONLY this DataFrame: {df_prompt}
                                        Follow these rules strictly:
                                        Only return the Pandas formula
                                        Do NOT provide any explanation or additional text
                                        the DataFrame is named df
                                        dont use ``` in the begin 
                                        Match logic and filtering precisely to the question
                                        Examples:
                                        Question 1: how many leads are cold?
                                        Answer: df[df['urgency'] == 'Cold'].shape[0]
                                        Question 2: list top 3 products
                                        Answer: df.nlargest(3, 'total revenue')['product name'].tolist()
                                        Question 3:give component names with their threshold
                                        Answer: df[['component name', 'threshold']].drop_duplicates()
                                        Question 4:list down types of driver
                                        Answer: df[df['component_name'].str.contains('driver', case=False, na=False)].drop_duplicates()
                            """]
                            response = get_gemini_response(chat_more, prompt1)
                            logger.info(response)
                            # pattern = r"```pandas\s*(.*?)\s*```"
                            # match = re.search(pattern, response, re.DOTALL)
                            match = response
                            result = []
                            if match:
                                code_to_execute = response
                                try:
                                    result = eval(code_to_execute)
                                except Exception as e:
                                    result = "Null"
                                    logger.warning(f"Error while executing code: {e}")

                            logger.info(result)

                            prompt2 = [f"""this is the question {chat_more} and this is the answer {result}"""]
                            ai_response = get_gemini_response("write answer properly", prompt2)
                            st.session_state.chat_history.insert(0, {"user": chat_more, "response": ai_response})
                            with open(CACHE_FILE, "w") as f:
                                json.dump(st.session_state.chat_history, f, indent=2)

                        if not df.empty and len(df.columns) >= 2 and len(df) > 1:
                            graph_type = st.radio("Choose a graph type:", ['Bar', 'Line', 'Scatter', 'Pie'])
                            logger.info(df.dtypes)
                            fig = None
                            if graph_type == 'Pie':
                                object_columns = df.select_dtypes(include='object').columns

                                # Filter for numerical columns (integer or float)
                                numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns

                                if len(object_columns) == 0:
                                    st.error("No object-type columns available for pie chart label.")
                                elif len(numerical_columns) == 0:
                                    st.error("No numerical columns available for pie chart values.")
                                else:
                                    name_col = st.selectbox("Select column for labels (names):", object_columns)
                                    value_col = st.selectbox("Select column for values.", numerical_columns)

                                    if name_col and value_col:
                                        fig = px.pie(df, names=name_col, values=value_col, title='Pie Chart')
                            else:
                                x_axis = st.selectbox("X Axis", df.columns, key="x_axis")
                                y_axis = st.multiselect("Y Axis", df.columns, default=[df.columns[1]],
                                                        key="y_axis")
                                if x_axis and y_axis:
                                    fig = getattr(px, graph_type.lower())(df, x=x_axis, y=y_axis,
                                                                          title=f'{graph_type} Chart')
                            if fig:
                                st.plotly_chart(fig)
                            else:
                                st.warning("Please select valid X and Y axis columns to generate the graph.")
                        else:
                            logger.info("DataFrame is empty or doesn't have enough columns.")

                    else:
                        st.write("No Data found")
                else:
                    st.write("Add CSV file")

        else:
            st.write("cache file not present")
    except Exception as e:
        logger.warning(f"error streamlit in pages Deep view {e}")
        st.error(f"No response")

with col2:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        st.success("Conversation ended and cache cleared.")

    st.subheader("📝 Conversation")

    # Inject scrollable container styling
    st.markdown("""
        <style>
        .scroll-box {
            height: 850px;
            overflow-y: scroll;
            padding: 10px;
            border: 1px solid rgb(38, 39, 48);
            border-radius: 10px;

        }
        .user-msg {
            font-weight: bold;
            # color: #3366cc;
            margin-bottom: 4px;
        }
        .bot-msg {
            font-weight: normal;
            # color: #000000;
            margin-bottom: 16px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Start of scrollable content
    chat_html = '<div class="scroll-box">'
    chat_html += '<p><strong>HEY THERE !!</strong></p>'

    # Loop through messages and append as HTML
    for msg in st.session_state.chat_history:
        chat_html += f'<div class="user-msg">🤓 ME: {msg["user"]}</div>'
        chat_html += f'<div class="bot-msg">🤖 BOT: {msg["response"]}</div>'

    chat_html += '</div>'  # Close scroll box
    st.markdown(chat_html, unsafe_allow_html=True)