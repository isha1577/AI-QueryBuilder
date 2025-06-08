# import streamlit as st
# import pandas as pd
# import json
# import os
# import google.generativeai as genai
# import tabulate
# import plotly.express as px
# from module.connection import update_fav, get_faq_id_by_question
# import re
#
# st.set_page_config(page_title="Abner Chatboard", layout="wide")
# genai.configure(api_key="AIzaSyD42VSIy3Ts5XJKUfD8wOWysNUPrObWnUE")
#
#
# @st.cache_resource
# def load_model():
#     return genai.GenerativeModel('models/gemini-1.5-pro-latest')
#
#
# def get_gemini_response(question, prompt):
#     try:
#         model = load_model()
#         response = model.generate_content([prompt[0], question])
#         return response.text
#     except Exception as e:
#         return f"Oops!! sorry I lost my way"
#
#
# CACHE_FILE = "chat_cache.json"
#
# # Initialize session state
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []
#
# # Load cache if it exists
# if os.path.exists(CACHE_FILE) and not st.session_state.chat_history:
#     try:
#         with open(CACHE_FILE, "r") as f:
#             st.session_state.chat_history = json.load(f)
#     except Exception as e:
#         st.warning(f"Failed to load cache: {e}")
#
# st.title("💬Chat with me")
# data_str = ""
# col1, col3, col2 = st.columns([1, 0.1, 1])
# with col1:
#     faq_id = ""
#     if "question" in st.session_state:
#         left, right = st.columns([1, 0.1])
#         with left:
#             st.markdown(f"###### Q.{st.session_state['question']}")
#         with right:
#             fav = st.button("❤️", help="Add to favorites")
#         if fav and st.session_state['question']:
#             faq_id = get_faq_id_by_question(st.session_state['question'])
#             update_fav(faq_id, True)
#             st.success("Added to favorites!")
#             st.rerun()
#
#     chat_more = st.text_input(label="Input", label_visibility="hidden", key="chat_more",
#                               placeholder="Ask a follow-up question")
#
#     try:
#
#         if not os.path.exists(CACHE_FILE):
#             with open(CACHE_FILE, "w") as f:
#                 json.dump([], f)
#         if os.path.exists(CACHE_FILE):
#             with open(CACHE_FILE, "r") as f:
#                 cache_data = json.load(f)
#                 if os.path.exists("temp_df.csv"):
#                     df = pd.read_csv("temp_df.csv")
#                     if df.shape == (1, 1):
#                         col_name = df.columns[0]
#                         for idx, value in enumerate(df[col_name]):
#                             st.code(f"{col_name}  : {value}")
#                     else:
#                         st.dataframe(df)
#                         if not df.empty and len(df.columns) >= 2:
#                             graph_type = st.radio("Choose a graph type:", ['Bar', 'Line', 'Scatter', 'Pie'])
#
#                             fig = None
#                             if graph_type == 'Pie':
#                                 name_col = st.selectbox("Select column for labels (names):", df.columns)
#                                 value_col = st.selectbox("Select column for values:", df.columns)
#                                 if name_col and value_col:
#                                     fig = px.pie(df, names=name_col, values=value_col, title="Pie Chart")
#
#                             else:
#                                 x_axis = st.selectbox("X Axis", df.columns, key="x_axis")
#                                 y_axis = st.multiselect("Y Axis", df.columns, default=[df.columns[1]],
#                                                         key="y_axis")
#                                 if x_axis and y_axis:
#                                     fig = getattr(px, graph_type.lower())(df, x=x_axis, y=y_axis,
#                                                                           title=f'{graph_type} Chart')
#                             if fig:
#                                 st.plotly_chart(fig)
#                             else:
#                                 st.warning("Please select valid X and Y axis columns to generate the graph.")
#                         else:
#                             print("DataFrame is empty or doesn't have enough columns.")
#
#                     data_str = df.to_markdown(index=False)
#
#                     if chat_more and chat_more.strip().startswith("+"):
#                         prompt1 = [f"""convert the asked question to pandas formula based on ONLY this DATA
#                                     {data_str} example Q. how many leads are cold? answer should be only : df[df['urgency'] == 'Cold'].shape[0]"""]
#                         response = get_gemini_response(chat_more, prompt1)
#                         print(response)
#                         pattern = r"```python\s*(.*?)\s*```"
#                         match = re.search(pattern, response, re.DOTALL)
#                         if match:
#                             code_to_execute = match.group(1)
#                             try:
#                                 result = eval(code_to_execute)
#                             except Exception as e:
#                                 result = f"Error while executing code: {e}"
#                     else:
#                         prompt1 = [f"""Continue a brief conversation as CHATBOT based on ONLY this DATA give
#                         the insights = {data_str} also if Data contains REVENUE or PRIZE or COST write in rupees"""]
#                         result = get_gemini_response(chat_more, prompt1)
#                     if chat_more:
#                         st.session_state.chat_history.insert(0, {"user": chat_more, "response": result})
#                         with open(CACHE_FILE, "w") as f:
#                             json.dump(st.session_state.chat_history, f, indent=2)
#                 else:
#                     st.write("csv file not existing")
#
#         else:
#             st.write("cache file not present")
#     except Exception as e:
#         st.error(f"Error generating response: {e}")
#
# with col2:
#     if st.button("Clear Chat"):
#         st.session_state.chat_history = []
#         if os.path.exists(CACHE_FILE):
#             os.remove(CACHE_FILE)
#         st.success("Conversation ended and cache cleared.")
#
#     st.subheader("📝 Conversation")
#
#     # Inject scrollable container styling
#     st.markdown("""
#         <style>
#         .scroll-box {
#             height: 850px;
#             overflow-y: scroll;
#             padding: 10px;
#             border: 1px solid rgb(38, 39, 48);
#             border-radius: 10px;
#
#         }
#         .user-msg {
#             font-weight: bold;
#             # color: #3366cc;
#             margin-bottom: 4px;
#         }
#         .bot-msg {
#             font-weight: normal;
#             # color: #000000;
#             margin-bottom: 16px;
#         }
#         </style>
#         """, unsafe_allow_html=True)
#
#     # Start of scrollable content
#     chat_html = '<div class="scroll-box">'
#     chat_html += '<p><strong>HEY THERE !!</strong></p>'
#
#     # Loop through messages and append as HTML
#     for msg in st.session_state.chat_history:
#         chat_html += f'<div class="user-msg">🤓 ME: {msg["user"]}</div>'
#         chat_html += f'<div class="bot-msg">🤖 BOT: {msg["response"]}</div>'
#
#     chat_html += '</div>'  # Close scroll box
#
#     st.markdown(chat_html, unsafe_allow_html=True)


import streamlit as st
import speech_recognition as sr

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        st.info("🎙️ Listening... Please speak clearly into your microphone.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        st.info("🔎 Recognizing...")
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "❌ Could not understand the audio."
    except sr.RequestError:
        return "⚠️ Could not request results from Google Speech Recognition service."

# Streamlit UI
st.title("🗣️ Speech to Text Converter")
st.write("Click the button below and start speaking.")

if st.button("Start Recording"):
    transcription = recognize_speech_from_mic()
    st.success("✅ Transcription Complete:")
    st.write(transcription)
