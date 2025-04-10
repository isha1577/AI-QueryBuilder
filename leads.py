from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()
# --------------------------------------------SIDEBAR-------------------------------------------

url = "http://localhost:8080/query"
# SQL query you want to send
payload = {
    "sqlQuery": f"select * from user"
}
# Make the POST request
response = requests.post(url, json=payload)
list = ''
list1 = ''
list2 = ''
if response.status_code == 200:
    data = response.json()  # already parsed JSON
    # print("Response JSON:", data)
    df = pd.DataFrame(data)
    st.sidebar.title("DASHBOARD")

    user_menu = st.sidebar.radio(
        'Select an Option',
        ('KAM NAME', 'INVENTORY', 'REGION')
    )
    selected_qoutation = ''

    if user_menu == 'KAM NAME':
        sql_kam = "SELECT * from user where ROLE_CODE ='ABNER_KAM';"
        # SQL query you want to send
        payload = {
            "sqlQuery": f"{sql_kam}"
        }

        # Make the POST request
        response_name = requests.post(url, json=payload)
        if response_name.status_code == 200:
            data1 = response_name.json()  # already parsed JSON
            kam = pd.DataFrame(data1)
            print(kam.columns)
            list1 = kam['USER_NAME'].unique()
        selected_kam = st.sidebar.selectbox("Select kam", list1)

        sql_kam = "SELECT STATUS from quotation_version;"
        # SQL query you want to send
        payload = {
            "sqlQuery": f"{sql_kam}"
        }
        # Make the POST request
        response_name = requests.post(url, json=payload)
        if response_name.status_code == 200:
            data1 = response_name.json()  # already parsed JSON
            product = pd.DataFrame(data1)
            print(product.columns)
            list = product['STATUS'].unique()
        selected_qoutation = st.sidebar.selectbox("Select Status", list)


        left_col, right_col = st.columns([2, 1])  # Wider left column
        sql1 = f"""SELECT 
    u.user_name,
    u.user_code,
    GROUP_CONCAT(DISTINCT am.account_name) AS account_names,
    
    -- Total distinct leads
    (SELECT COUNT(DISTINCT lt.lead_code)
     FROM lead_transactions lt
     WHERE lt.created_by = u.user_code) AS total_leads,
    
    -- Total distinct quotations
    (SELECT COUNT(DISTINCT q.quotation_code)
     FROM lead_transactions lt
     JOIN quotation q ON lt.lead_code = q.lead_code
     WHERE lt.created_by = u.user_code) AS total_quotations,
    
    -- Conversion rate
    (SELECT 
        (COUNT(DISTINCT q.quotation_code) * 1.0 / NULLIF(COUNT(DISTINCT lt.lead_code), 0)) * 100
     FROM lead_transactions lt
     LEFT JOIN quotation q ON lt.lead_code = q.lead_code
     WHERE lt.created_by = u.user_code) AS conversion_rate_percentage,
    
    -- Total orders
    (SELECT COUNT(DISTINCT q.quotation_code)
     FROM lead_transactions lt
     JOIN quotation q ON lt.lead_code = q.lead_code
     WHERE lt.MODIFIED_BY = u.user_code AND lt.status = 'ACTIVE') AS total_orders,
    
    -- Total revenue
    (SELECT SUM(qv.total_cost)
     FROM (
         SELECT DISTINCT q.quotation_code
         FROM lead_transactions lt
         JOIN quotation q ON lt.lead_code = q.lead_code
         WHERE lt.created_by = u.user_code
     ) AS qcodes
     JOIN quotation_version qv ON qcodes.quotation_code = qv.quotation_code) AS total_revenue,
    
    -- Total quotation_version entries with given status
    (SELECT COUNT(*) 
     FROM quotation_version qv2 
     WHERE qv2.created_by = u.user_code 
       AND qv2.status = '{selected_qoutation}'
    ) AS total_entries_with_status
    
    FROM user u
    JOIN account_master am ON am.account_manager = u.user_code
    WHERE u.user_name = '{selected_kam}'
    GROUP BY u.user_name, u.user_code;
    """
        kam1 = ''
        payload2 = {
            "sqlQuery": f"{sql1}"
        }

        # Make the POST request
        response_name1 = requests.post(url, json=payload2)

        if response_name1.status_code == 200:
            data2 = response_name1.json()
            kam1 = pd.DataFrame(data2)


            with left_col:
                def format_number(num):
                    for unit in ['', 'K', 'M', 'B', 'T', 'P']:
                        if abs(num) < 1000:
                            return f"{num:.2f}{unit}"
                        num /= 1000
                    return f"{num:.2f}E"


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

                # Donut chart using Plotly
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
            # SQL query you want to send
            payload = {
                "sqlQuery": f"{sql_revenue}"
            }

            # Make the POST request
            response_name = requests.post(url, json=payload)
            if response_name.status_code == 200:
                data_df = response_name.json()  # already parsed JSON
                kam = pd.DataFrame(data_df)
                # kam['revenue_date'] = pd.to_datetime(kam['revenue_date'])

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

else:
    print("Failed with status code:", response.status_code)
    print("Error message:", response.text)
