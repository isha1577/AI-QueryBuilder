import streamlit as st
import base64
import speech_recognition as sr

st.set_page_config(page_title="Abner Chatboard")
from module.connection import insert_or_increment_question, fetch_fav, update_fav, fetch_data, get_faq_id_by_question, get_credentials, fetch_suggestions
from module.chatbot import get_gemini_response, admin_prompt , user_prompt
import streamlit_authenticator as stauth


def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎤 Listening... please speak.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        st.info("📝 Recognizing...")
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "❌ Could not understand audio"
    except sr.RequestError:
        return "⚠️ API unavailable"


def process_question_and_display(question, prompt, cache):
    try:
        del st.session_state['selected_question']
        generated_sql = get_gemini_response(question.strip(), prompt)
        print(generated_sql)

        fetch_data(generated_sql)
        st.session_state["question"] = question
        st.success("Data generated!")
        st.sidebar.page_link("pages/Calcutate.py", label="Calculator")
        st.switch_page("pages/Calcutate.py")

    except Exception as e:
        print(f"error message = {e}")
        st.error(f"I lost my way")


credentials = get_credentials()
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name='some_cookie_name',
    key='some_signature_key',
    cookie_expiry_days=1
)
cache = st.session_state.get('cache', False)

name, authentication_status, username = authenticator.login('Login', 'main')
st.session_state["authentication_status"] = authentication_status
st.session_state["username"] = username

if authentication_status is False:
    st.error("❌ Username/password is incorrect.")
elif authentication_status is None:
    st.warning("🔐 Please enter your username and password.")
elif authentication_status is True:
    st.sidebar.success(f"Welcome {name}!")
    if username.lower() == "admin":
        prompt = admin_prompt
    else:
        prompt = user_prompt.format(myname=name)

    with open("abstractLayer.png", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{encoded}" width="80" style="margin-right: 10px;">
            <h1 style="margin: 0;">What’s on your mind?</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    if 'question' not in st.session_state:
        st.session_state.question = ""

    mic_clicked = st.button("🎤 Click to Speak")
    if mic_clicked:
        st.session_state.question = recognize_speech()

    question = st.text_input("Transcribed Text", value=st.session_state.question, key="transcription_input")

    if question:
        matching_suggestions = fetch_suggestions(question)
        if matching_suggestions:
            for item in matching_suggestions:
                if st.button(item, key=f"select_{item}"):
                    st.session_state.question = item

    col1, col2 = st.columns([1, 0.1])
    faq_id = ""

    with col1:
        submit = st.button("Submit")

    if submit and question.strip():
        faq_id = insert_or_increment_question(question.strip())
        process_question_and_display(question.strip(), prompt, False)

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
        # st.write(f"Q. {st.session_state.selected_question}")
        process_question_and_display(st.session_state.selected_question, prompt, True)

authenticator.logout('Logout', 'sidebar')