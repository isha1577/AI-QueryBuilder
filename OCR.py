from dotenv import load_dotenv

load_dotenv()
import json
import streamlit as st
import os
import google.generativeai as genai
# import numpy as np
import pandas as pd

# genai.configure(api_key=my_api_key)
genai.configure(api_key="AIzaSyC2ihGO4LEFAJ_FVuZrKgtGOEbu0bEFo7U")


def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    response = model.generate_content([prompt[0], question])
    return response.text


prompt = [
    """
    You are an expert in extracting structured data from input text.
    Always return the response as a JSON object formatted inside triple backticks (```)
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

st.set_page_config(page_title="i can retrive any DATA for OCR")
st.header("gemini app to retrieve data from OCR text")

question = st.text_input("Input:", key="input")

submit = st.button("FEED ME DATA")

if submit:
    response = get_gemini_response(question, prompt)

    if response:
        # Extract JSON from backticks (```)
        if "```" in response:
            response = response.split("```")[1].strip()  # Get JSON part only

        try:
            data = json.loads(response)  # Parse JSON

            # Display raw JSON
            st.json(data)

            # Convert JSON to Pandas DataFrame
            df = pd.json_normalize(data)  # Flatten nested JSON

            # Display DataFrame as a table
            st.write("### Extracted Data Table")
            st.dataframe(df)  # Show table in Streamlit

        except json.JSONDecodeError as e:
            st.error(f"JSON Parsing Error: {e}")
            st.write("Raw Response:", response)  # Show response for debugging
    else:
        st.error("No response received!")

    # st.write(f"**Generated TABLE:** `{response}`")
    # data = json.loads(response)
    # categories = sorted(set(item.get("category", "") for item in data))
    # for category in categories:
    #     st.subheader(category)
    #     for item in data:
    #         if item.get("category") == category:
    #             for key, value in item.items():
    #                 if key != "category" and value:
    #                     st.write(f"**{key.replace('_', ' ').title()}**: {value}")
    #             st.write("---")
    # data = json.loads(response)
    # for key, value in data.items():
    #     if isinstance(value, str):
    #         st.write(f"**{key.replace('_', ' ').title()}**: {value}")
    #     elif isinstance(value, list):
    #         st.subheader(key.replace('_', ' ').title())
    #         for index, item in enumerate(value):
    #             st.markdown(f"### {key.replace('_', ' ').title()} {index + 1}")
    #             for sub_key, sub_value in item.items():
    #                 if isinstance(sub_value, list):
    #                     st.markdown(f"**{sub_key.replace('_', ' ').title()}**:")
    #                     for sub_item in sub_value:
    #                         st.markdown(f"- {sub_item}")
    #                 else:
    #                     st.write(f"**{sub_key.replace('_', ' ').title()}**: {sub_value}")
    #             st.write("---")