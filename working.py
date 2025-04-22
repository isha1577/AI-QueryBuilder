from dotenv import load_dotenv
import streamlit as st

st.set_page_config(page_title="i can retrive any sql query", layout="centered")
import plotly.graph_objects as go
import json
import google.generativeai as genai
import pandas as pd
import requests
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth

load_dotenv()
genai.configure(api_key="AIzaSyC2ihGO4LEFAJ_FVuZrKgtGOEbu0bEFo7U")


@st.cache_resource
def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')


def get_gemini_response(question, prompt):
    model = load_model()
    response = model.generate_content([prompt[0], question])
    return response.text


# Define prompt
prompt = ["""
YOU ARE AN EXPERT just Convert English questions to SQL queries:
YOU ARE GIVEN SQL database  that have 4 tables  
lead_transactions ( created_by,created_on, urgency, scope, lead_code, category)
user (user_code, user_name, mobile_number )  
lead_contact ( created_by, contact_name, contact_designation, lead_code, contact_mobile_number,created_on)
quotation ( created_by, lead_code, quotation_code, urgency, created_on )
quotation_version ( created_by, quotation_code, total_cost, packaging_cost, transportation_cost, quotation_scope_code,created_on )
user_code is equal to created_by in other tables
the questions will be something like this :
question 1. Get all leads created by a specific user (e.g., user code 'KJ9979')
your answer should be:
SELECT * FROM lead_transactions WHERE created_by = 'KJ9979';
question 2. Get the contact details for a specific lead e.g. lead code is 'LD2408078103'
your answer should be:
SELECT contact_name, contact_designation, contact_mobile_number FROM lead_contact WHERE lead_code = 'LD2408078103';
question 3. month wise how many leads are generated?
your answer should be:
SELECT DATE_FORMAT(created_on, '%Y-%m-01') AS month, COUNT(*) AS lead_count FROM lead_transactions WHERE created_on IS NOT NULL GROUP BY DATE_FORMAT(created_on, '%Y-%m-01') ORDER BY month;
question 4. who are the Top 10 performing Salespersons or KAMs
your answer should be :
SELECT u.user_name, u.mobile_number, SUM(qv.total_cost) AS total_sales_value, COUNT(DISTINCT q.quotation_code) AS total_quotations, COUNT(DISTINCT lt.lead_code) AS total_leads FROM quotation_version qv JOIN quotation q ON qv.quotation_code = q.quotation_code JOIN lead_transactions lt ON q.lead_code = lt.lead_code JOIN user u ON q.created_by = u.user_code GROUP BY u.user_name, u.mobile_number ORDER BY total_sales_value DESC LIMIT 10;
question 5. What professions have the highest number of leads in the system?
your answer should be :
SELECT contact_designation, COUNT(*) AS lead_count FROM lead_contact WHERE contact_designation IS NOT NULL GROUP BY contact_designation ORDER BY lead_count DESC;
question 6. what is the total sales revenue ?
your answer should be :
SELECT DATE_FORMAT(lt.created_on, '%Y-%m') AS month, SUM(qv.total_cost) AS total_revenue FROM lead_transactions lt JOIN quotation q ON lt.lead_code = q.lead_code JOIN quotation_version qv ON q.quotation_code = qv.quotation_code GROUP BY DATE_FORMAT(lt.created_on, '%Y-%m') ORDER BY month;

the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
"""]

names = ['Admin', 'Bob']
usernames = ['admin', 'bob']
passwords = ['password123', 'root456']  # In production, use environment variables or hashed passwords directly

# 2. Hash the passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# 3. Create the authenticator object
authenticator = stauth.Authenticate(
    credentials={
        "usernames": {
            usernames[0]: {
                "name": names[0],
                "password": hashed_passwords[0],
            },
            usernames[1]: {
                "name": names[1],
                "password": hashed_passwords[1],
            },
        }
    },
    cookie_name='some_cookie_name',
    key='some_signature_key',
    cookie_expiry_days=1
)

# 4. Login
name, authentication_status, username = authenticator.login('Login', 'main')

# 5. Display login status
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome {name}!")

    st.header("Ask Me Anything")
    question = st.text_input("Input:", key="input")
    submit = st.button("Extract")

    # ----------------------------------------gemini api-----------------------------------------------------
    if submit:
        response = get_gemini_response(question, prompt)
        url = "http://localhost:8080/query"
        payload = {
            "sqlQuery": f"{response}"
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()  # already parsed JSON

            df = pd.DataFrame(data)
            st.dataframe(df)

            if 'urgency' in df.columns:
                urgency_counts = df['urgency'].value_counts().reset_index()
                urgency_counts.columns = ['urgency', 'count']

                # Plotting
                fig = px.bar(
                    urgency_counts,
                    x='urgency',
                    y='count',
                    color='urgency',
                    title='Lead Count by Urgency',
                    labels={'count': 'Number of Leads', 'urgency': 'Urgency'},
                    template='plotly_white'
                )

                # Streamlit app layout
                st.title("Lead Urgency Dashboard")
                st.plotly_chart(fig)

            if 'month' in df.columns and 'lead_count' in df.columns:
                df['month'] = pd.to_datetime(df['month'])

                df = df.sort_values('month')

                # Plot
                fig = px.line(
                    df,
                    x='month',
                    y='lead_count',
                    title='Monthly Lead Volume',
                    labels={'month': 'Month', 'lead_count': 'Number of Leads'},
                    markers=True,
                    template='plotly_white'
                )


                st.title("Lead Trends Over Time")
                st.plotly_chart(fig)

            if 'contact_designation' in df.columns:
                df = df.sort_values('lead_count', ascending=True)
                fig = px.bar(
                    df,
                    x='lead_count',
                    y='contact_designation',
                    orientation='h',
                    title='Lead Count by Contact Designation',
                    labels={'lead_count': 'Number of Leads', 'contact_designation': 'Designation'},
                    template='plotly_white'
                )
                st.plotly_chart(fig)

            if 'month' in df.columns and 'total_revenue' in df.columns:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(df['month'], df['total_revenue'], color='skyblue')
                ax.set_title("Monthly Revenue")
                ax.set_xlabel("Month")
                ax.set_ylabel("Total Revenue")
                plt.xticks(rotation=45)
                ax.grid(axis='y', linestyle='--', alpha=0.6)

                st.pyplot(fig)

        else:
            print("Failed with status code:", response.status_code)
            print("System records not found")

elif authentication_status is False:
    st.error("❌ Username/password is incorrect.")
elif authentication_status is None:
    st.warning("🔐 Please enter your username and password.")
