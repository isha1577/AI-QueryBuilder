from dotenv import load_dotenv
import streamlit as st
import os
import json
import google.generativeai as genai
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key="AIzaSyC2ihGO4LEFAJ_FVuZrKgtGOEbu0bEFo7U")

# Define prompt
prompt = [
    """
    You are an expert in extracting structured data from input text.
    Always return the response as a JSON object formatted inside triple backticks (```).
    Example format:
    ```
    {
      "personal_information": {
        "name": "Pablo Neruda",
        "birthdate": "12/07/1904",
        "location": "Santiago de Chile, Chile",
        "phone": "(999) 999 9999",
        "email": "hello@kickresume.com",
        "website": "www.kickresume.com"
      }
    }
    ```
    """
]

# Streamlit UI setup
st.set_page_config(page_title="Extract Data from OCR")
st.header("Gemini App for OCR Data Extraction")

# File uploader
uploaded_file = st.file_uploader("Upload a text or CSV file", type=["txt", "csv"])

question = st.text_input("Enter your query:", key="input")
submit = st.button("Extract Data")
text_data =""
if submit and uploaded_file:
    # Read the file content
    if uploaded_file.name.endswith(".txt"):
        text_data = uploaded_file.read().decode("utf-8")  # Read text file
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)  # Read CSV file
        text_data = df.to_json()  # Convert CSV to JSON string

    # Prepare input for the model
    full_input = f"{prompt[0]}\n\nExtract information from:\n{text_data}"

    # Generate response
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    response = model.generate_content([full_input, question])

    if response:
        # Extract JSON from response
        response_text = response.text

        if "```" in response_text:
            response_text = response_text.split("```")[1].strip()

        try:
            extracted_data = json.loads(response_text)
            st.json(extracted_data)  # Display extracted data as JSON

            # Convert to DataFrame and display table
            df_extracted = pd.json_normalize(extracted_data)
            st.write("### Extracted Data Table")
            st.dataframe(df_extracted)

        except json.JSONDecodeError as e:
            st.error(f"JSON Parsing Error: {e}")
            st.write("Raw Response:", response_text)
    else:
        st.error("No response received!")
elif submit and not uploaded_file:
    st.error("Please upload a file first.")
