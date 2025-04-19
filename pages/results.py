import streamlit as st
import pandas as pd
import os
import plotly.express as px
import google.generativeai as genai
import tabulate
st.set_page_config(page_title="Results")

genai.configure(api_key="AIzaSyC2ihGO4LEFAJ_FVuZrKgtGOEbu0bEFo7U")


@st.cache_resource
def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')


prompt = ["""  I am giving you the Data as input as table i want you to give me the insghts upon that data in 3-4 lines explain in a simple manner"""]


def get_gemini_response(question, prompt):
    model = load_model()
    response = model.generate_content([prompt[0], question])
    return response.text



st.title("📊 Query Results")
if os.path.exists("temp_df.csv"):
    st.subheader("📄 Cached Output:")
    df = pd.read_csv("temp_df.csv")
    st.dataframe(df)

    if not df.empty and len(df.columns) >= 2:
        graph_type = st.radio("Choose a graph type:", ['Bar', 'Line', 'Scatter', 'Pie'])

        fig = None
        if graph_type == 'Pie':
            name_col = st.selectbox("Select column for labels (names):", df.columns)
            value_col = st.selectbox("Select column for values:", df.columns)
            if name_col and value_col:
                fig = px.pie(df, names=name_col, values=value_col, title="Pie Chart")

        else:
            x_axis = st.selectbox("X Axis", df.columns, key="x_axis")
            y_axis = st.multiselect("Y Axis", df.columns, default=[df.columns[1]], key="y_axis")
            if x_axis and y_axis:
                fig = getattr(px, graph_type.lower())(df, x=x_axis, y=y_axis,
                                                      title=f'{graph_type} Chart')

        if fig:
            st.plotly_chart(fig)
        else:
            st.warning("Please select valid X and Y axis columns to generate the graph.")
    else:
        st.warning("DataFrame is empty or doesn't have enough columns.")

    submit = st.button("EXPLAIN")
    if submit:
        data_as_string = df.to_markdown(index=False)  # Or use df.to_csv(index=False)
        response = get_gemini_response(data_as_string, prompt)
        st.markdown(response)

else:
    st.warning("No DATA found.")
