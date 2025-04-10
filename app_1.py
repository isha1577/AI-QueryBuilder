from dotenv import load_dotenv
import streamlit as st

st.set_page_config(page_title="i can retrive any sql query")
import plotly.graph_objects as go
import json
import google.generativeai as genai
import pandas as pd
import requests
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Configure Gemini API
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

url = "http://localhost:8080/query"
payload = {
    "sqlQuery": f"select * from user"
}
response = requests.post(url, json=payload)
list = ''
list1 = ''
list2 = ''
user_menu=''
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    st.sidebar.title("DASHBOARD")

    user_menu = st.sidebar.radio(
        'Select an Option',
        ('KAM NAME', 'QUOTATION', 'INVENTORY')
    )

    selected_qoutation = ''

    if user_menu == 'KAM NAME':
        sql_kam = "SELECT * from user where ROLE_CODE ='ABNER_KAM';"
        payload = {
            "sqlQuery": f"{sql_kam}"
        }
        response_name = requests.post(url, json=payload)
        selected_kam=''
        if response_name.status_code == 200:
            data1 = response_name.json()
            try:
                kam = pd.DataFrame(data1)
                print(kam.columns)
                list1 = kam['USER_NAME'].unique()
                selected_kam = st.sidebar.selectbox("Select kam", list1)
                status_map = {
                    'Finalized': 'FINALIZED',
                    'Action Awaited': 'SUBMIT_TO_CRM_QUOTATION',
                    'Sent Back to KAM': 'SUBMIT_TO_KAM_QUOTATION',
                    'Sent Back to CRM': 'SUBMIT_BACK_TO_CRM_QUOTATION',
                    'SO Generated': 'SUBMIT_TO_KAM_QUOTATION_APPROVED',
                    'Awaiting SO Approval': 'SUBMIT_TO_CRM_SALES_ORDER',
                    'Initiate Work Order': 'SUBMIT_TO_KAM_SALES_ORDER_APPROVED',
                    'SO Reassigned': 'SUBMIT_TO_KAM_SALES_ORDER_REJECTED',
                    'Good for PO': 'SUBMIT_TO_CRM_PRODUCTION',
                    'Cancelled': 'CANCELLED',
                    'Production Completed': 'PRODUCTION_COMPLETED',
                    'Drafted': 'DRAFT',
                    'Preview': 'PREVIEW',
                    'Completed': 'COMPLETED',
                    'In Progress': 'IN_PROGRESS',
                    'Prize Apporval Waiting': 'PRICE_APPROVAL_AWAITED'
                }
                status_list = [key for key in status_map]
                selected_qoutation = st.sidebar.selectbox("Select Status", status_list)
                internal_status = status_map[selected_qoutation]

                left_col, right_col = st.columns([2, 1])
                sql1 = f"""SELECT 
                    u.user_name,
                    u.user_code,
                    GROUP_CONCAT(DISTINCT am.account_name) AS account_names,
                    (SELECT COUNT(DISTINCT lt.lead_code)
                     FROM lead_transactions lt
                     WHERE lt.created_by = u.user_code) AS total_leads,
                    (SELECT COUNT(DISTINCT q.quotation_code)
                     FROM lead_transactions lt
                     JOIN quotation q ON lt.lead_code = q.lead_code
                     WHERE lt.created_by = u.user_code) AS total_quotations,
                    (SELECT 
                        (COUNT(DISTINCT q.quotation_code) * 1.0 / NULLIF(COUNT(DISTINCT lt.lead_code), 0)) * 100
                     FROM lead_transactions lt
                     LEFT JOIN quotation q ON lt.lead_code = q.lead_code
                     WHERE lt.created_by = u.user_code) AS conversion_rate_percentage,
                    (SELECT COUNT(DISTINCT q.quotation_code)
                     FROM lead_transactions lt
                     JOIN quotation q ON lt.lead_code = q.lead_code
                     WHERE lt.MODIFIED_BY = u.user_code AND lt.status = 'ACTIVE') AS total_orders,
                    (SELECT SUM(qv.total_cost)
                     FROM (
                         SELECT DISTINCT q.quotation_code
                         FROM lead_transactions lt
                         JOIN quotation q ON lt.lead_code = q.lead_code
                         WHERE lt.created_by = u.user_code
                     ) AS qcodes
                     JOIN quotation_version qv ON qcodes.quotation_code = qv.quotation_code) AS total_revenue,
                    (SELECT COUNT(*) 
                     FROM quotation_version qv2 
                     WHERE qv2.created_by = u.user_code 
                       AND qv2.status = '{internal_status}') AS total_entries_with_status
                    FROM user u
                    JOIN account_master am ON am.account_manager = u.user_code
                    WHERE u.user_name = '{selected_kam}'
                    GROUP BY u.user_name, u.user_code;
                """

                kam1 = ''
                payload2 = {
                    "sqlQuery": f"{sql1}"
                }
                response_name1 = requests.post(url, json=payload2)
                if response_name1.status_code == 200:
                    data2 = response_name1.json()
                    try:
                        kam1 = pd.DataFrame(data2)
                        with left_col:
                            def format_number(num):
                                abs_num = abs(num)
                                if abs_num < 1_000:
                                    return f"{num:.2f}"
                                elif abs_num < 1_00_000:
                                    return f"{num:.1f}K"
                                elif abs_num < 1_00_00_000:
                                    return f"{num / 1_00_000:.1f}L"
                                elif abs_num < 1_00_00_00_000:
                                    return f"{num / 1_00_00_000:.1f}Cr"
                                else:
                                    return f"{num / 1_00_00_00_000:.1f}TCr"


                            title_value = kam1.iloc[0, 7]
                            number = format_number(title_value)
                            title_value1 = kam1.iloc[0, 6]
                            title_value2 = kam1.iloc[0, 2]
                            title_value3 = kam1.iloc[0, 8]
                            print(title_value2)

                            col1, col2, col3 = st.columns(3)
                            col1.metric("Total Revenue", str(number))
                            col2.metric("Total Orders", str(title_value1))
                            col3.metric("Quotations", str(title_value3))

                            unique_customers = [cust.strip().title() for cust in title_value2.split(",")]
                            st.markdown("### 🧑‍💼 Unique Customers")
                            for customer in unique_customers:
                                st.markdown(f"- {customer}")

                        with right_col:
                            title_value2 = kam1.iloc[0, 5]
                            non_conversion_rate = 100 - title_value2

                            fig = go.Figure(data=[go.Pie(
                                labels=["Converted", "Not Converted"],
                                values=[title_value2, non_conversion_rate],
                                hole=0.4,
                                marker=dict(colors=["green", "orange"]),
                                textinfo='percent'
                            )])

                            fig.update_layout(
                                title_text="🔁 Conversion Rate",
                                showlegend=False,
                                width=400,
                                height=400
                            )

                            st.plotly_chart(fig)
                    except Exception as e:
                        st.error(f"System Doesn't have any record")
                sql_revenue = f"""SELECT 
        u.user_code,
        u.user_name, -- optional: user name
        DATE(qv.created_on) AS revenue_date,
        SUM(qv.total_cost) AS daily_revenue
        FROM lead_transactions lt
        JOIN quotation q ON lt.lead_code = q.lead_code
        JOIN quotation_version qv ON q.quotation_code = qv.quotation_code
        JOIN user u ON lt.created_by = u.user_code where user_name='{selected_kam}'
        GROUP BY u.user_code, u.user_name, DATE(qv.created_on)  ORDER BY u.user_code, revenue_date;
        """
                payload = {
                    "sqlQuery": f"{sql_revenue}"
                }
            # Make the POST request
                response_name = requests.post(url, json=payload)
                print(f"--------{response_name}-----------------here")
                if response_name.status_code == 200:
                    data_df = response_name.json()  # already parsed JSON
                    kam = pd.DataFrame(data_df)
                    fig = px.line(
                        kam,
                        x='revenue_date',
                        y='daily_revenue',
                        color='user_code',  # Or use 'name' if you prefer user names
                        markers=True,
                        title='Daily Revenue per User',
                        labels={'revenue_date': 'Date', 'daily_revenue': 'Revenue'}
                    )

                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"System Doesn't have any record")

    if user_menu == 'INVENTORY':
        product = ''
        sql_product = "SELECT * from product_master"
        url = "http://localhost:8080/query"
        # SQL query you want to send
        payload = {
            "sqlQuery": f"{sql_product}"
        }
        # Make the POST request
        response_name = requests.post(url, json=payload)
        if response_name.status_code == 200:
            data1 = response_name.json()  # already parsed JSON
            product = pd.DataFrame(data1)
            print(product.columns)
        selected_product = st.sidebar.selectbox("Select kam", product['product_name'].unique())

    st.header("gemini app to retrieve SQL data")

    question = st.text_input("Input:", key="input")

    submit = st.button("Ask the question")

# ----------------------------------------gemini api-----------------------------------------------------
    if submit:
        response = get_gemini_response(question, prompt)
        st.write(f"**Generated SQL Query:** {response}")

        url = "http://localhost:8080/query"
        # SQL query you want to send
        payload = {
            "sqlQuery": f"{response}"
        }
        # Make the POST request
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()  # already parsed JSON
            # print("Response JSON:", data)
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

                # Streamlit app
                st.title("Lead Trends Over Time")
                st.plotly_chart(fig)

            if 'contact_designation' in df.columns:
                    df = df.sort_values('lead_count', ascending=True)  # for horizontal bar

                    # Plot
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
            print("Error message:", response.text)
