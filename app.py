from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import sqlite3
import google.generativeai as genai
# import numpy as np
import pandas as pd

# genai.configure(api_key=my_api_key)
genai.configure(api_key="AIzaSyC2ihGO4LEFAJ_FVuZrKgtGOEbu0bEFo7U")


# function to load google model to create sql query

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    response = model.generate_content([prompt[0], question])
    return response.text


def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows


# prompt=[
#     """
#     You are an expert in converting English questions to SQL query!
#     The SQL database student has 2 tables name PROJECT, SALES
#     and PROJECT table has the following columns NAME, CLASS, SECTION and MARKS \n\nFor example,
#     \nExample 1 How many entries of records are present
#     the SQL command will be something like this SELECT COUNT(*) FROM STUDENT ;
#     TECHERS table has the following columns NAME, CLASS and TECID \n\nFor example,
#     \nExample 1 How many entries of records are present
#     the SQL command will be something like this SELECT COUNT(*) FROM TEACHERS ;
#     nExample 3 Tell me all the students studying in Data Science class?, the SQL command will be something
#     like this SELECT * FROM STUDENT where CLASS="Data Science";
#     nExample 4 Tell me teacher id  that teaches Chemistry class?, the SQL command will be something
#     like this SELECT TECID FROM TEACHERS where CLASS="Chemistry";
#
#      the sql code should not have ```sql in beginning and ``` in the end
#     DONT USE ```sql in beginning and ``` in end
#     only give SQL QUERY TO EXECUTE
#     """
# ]


prompt = [
    """
YOU ARE AN EXPERT just Convert English questions to SQL queries:
YOU ARE GIVEN SQL database company that have 4 tables  
PROJECTS (project_id, company_id, name, start_date, end_date, status, budget)
PROJECT_ASSIGNMENTS (assignment_id, project_id, employee_id, role, date_assigned)
CLIENTS (client_id, company_id, name, contact_person, email, phone)
SALES (sale_id, company_id, client_id, employee_id, amount, date)
the questions will be something like this :
Example 1: How many project records are present?
and answer to be given in SQL query like this:
SELECT COUNT(*) FROM PROJECTS;

Example 2: How many sales transactions have been recorded?
SELECT COUNT(*) FROM SALES;

Example 3: Show all ongoing projects.
SELECT * FROM PROJECTS WHERE status = 'Ongoing';

Example 4: Get the names of clients associated with company ID 101.
SELECT name FROM CLIENTS WHERE company_id = 101;

     the sql code should not have ```sql in beginning and ``` in the end 
    DONT USE ```sql in beginning and ``` in end 
    only give SQL QUERY TO EXECUTE
    """
]

st.set_page_config(page_title="i can retrive any sql query")
st.header("gemini app to retrieve SQL data")

question = st.text_input("Input:", key="input")

submit = st.button("Ask the question")

# if submit:
#     response=get_gemini_response(question,prompt)
#     print(response)
#     # SELECT NAME from STUDENT   get the name from respose and set it as table header 
#     data=read_sql_query(response,"student.db")
#     st.subheader("The response is")
#     if isinstance(data,list) and len(data)>0:
#         df=pd.DataFrame(data)
#         st.dataframe(df)


# for row in data:
#     print(row)
#     st.header(row)

if submit:
    response = get_gemini_response(question, prompt)
    st.write(f"**Generated SQL Query:** {response}")

    # Fetch data from database
    data = read_sql_query(response, "company.db")

    if isinstance(data, list) and len(data) > 0:
        df = pd.DataFrame(data)
        st.subheader("Query Result:")
        st.dataframe(df)

        # Check if the data is numeric for visualization
        if 1 in df.columns:
            st.subheader("Bar Graph Representation:")
            st.bar_chart(df.set_index(0)[1])  # Plot NAME vs MARKS
        else:
            st.write("No numerical data found to plot.")
    else:
        st.write("No data found.")
