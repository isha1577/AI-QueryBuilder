from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()
# --------------------------------------------SIDEBAR-------------------------------------------

url = "http://localhost:8080/query"
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
        ('KAM NAME', 'QUOTATION', 'INVENTORY')
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
                col3.metric("Quotations Handled", str(title_value3))
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

    if user_menu == 'QUOTATION':
        product = ''
        sql_product = """SELECT 
    qvpm.qv_product_mapping_id,
    qvpm.created_by,
    u.user_name,
    qvpm.quotation_version_code,
    qvpm.product_code,
    qvpm.product_quantity,
    qvpm.product_discount,
    qvpm.product_total_price,
    qvpm.product_retail_price,
    qvpm.product_kam_price,

    qvc.commission_display_percent,

    qvpp.product_paramter_name,
    qvpp.product_paramter_value,
    qvpp.product_outer_diameter,
    qvpp.product_paramter_price,

    pm.brand_name,
    pm.product_desc,
    pm.retail_price AS master_retail_price,
    pm.lp_price,
    pm.msp_price,
    pm.product_name,

    qv.status  -- Added status from quotation_version

FROM quotation_version_product_mapping qvpm

LEFT JOIN quotation_version_commission qvc 
    ON qvpm.quotation_version_code = qvc.quotation_version_code 
    AND qvpm.created_by = qvc.created_by

LEFT JOIN quotation_version_product_parameter_mapping qvpp 
    ON qvpm.quotation_version_code = qvpp.quotation_version_code 
    AND qvpm.product_code = qvpp.product_code 
    AND qvpm.created_by = qvpp.created_by

LEFT JOIN product_master pm 
    ON qvpm.product_code = pm.product_code

LEFT JOIN user u 
    ON qvpm.created_by = u.user_code

LEFT JOIN quotation_version qv 
    ON qvpm.quotation_version_code = qv.quotation_version_code;  -- Join to get status
"""
        url = "http://localhost:8080/query"
        # SQL query you want to send
        payload = {
            "sqlQuery": f"{sql_product}"
        }
        print(payload)
        # Make the POST request
        response_name = requests.post(url, json=payload)
        if response_name.status_code == 200:
            data1 = response_name.json()  # already parsed JSON
            df = pd.DataFrame(data1)
            print(df.columns)
            # Calculate total parameter price per row
            df["parameter_total_price_per_unit"] = df["product_paramter_price"]
            df["parameter_total_price_all"] = df["product_paramter_price"] * df["product_quantity"]

            # Calculate retail base price total
            df["base_retail_price_all"] = df["master_retail_price"] * df["product_quantity"]

            # Final estimated price per row
            df["estimated_total_price"] = df["parameter_total_price_all"] + df["base_retail_price_all"]

            # Grouped by quotation
            grouped = df.groupby("quotation_version_code").agg({
                "product_quantity": "sum",
                "parameter_total_price_all": "sum",
                "base_retail_price_all": "sum",
                "estimated_total_price": "sum"
            }).reset_index()

            st.subheader("📄 Quotation-Level Summary")
            st.dataframe(grouped, use_container_width=True)

            # Total revenue estimation
            total_revenue = grouped["estimated_total_price"].sum()
            st.metric("💰 Total Revenue (Estimated)", f"₹{total_revenue:,.0f}")

            # sales distribution
            st.subheader("🧾 Status Distribution")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.bar(
                status_counts,
                x='Count',
                y='Status',
                color='Status',
                title="Status Count",
                orientation='h'  # Optional: makes it horizontal
            )
            fig_status.update_layout(showlegend=False)  # 🔥 Hides the legend
            st.plotly_chart(fig_status)

            # Pie chart: Parameter cost impact
            st.subheader("🔧 Parameter Cost Distribution")
            param_cost = df.groupby("product_paramter_name")["parameter_total_price_all"].sum().reset_index()
            fig = px.pie(
                param_cost,
                names="product_paramter_name",
                values="parameter_total_price_all",
                title="Total Parameter Value Impact"
            )
            fig.update_traces(textinfo='none')  # Hide text labels on the pie chart
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📦 Quotation Version Occurrences")
            quotation_counts = df['quotation_version_code'].value_counts().reset_index()
            quotation_counts.columns = ['quotation_version_code', 'product_quantity']
            fig_quotation = px.bar(
                quotation_counts,
                x='quotation_version_code',
                y='product_quantity',
                title="Quotation Version Code Frequency",
                text='product_quantity',
                color='quotation_version_code'
            )

            fig_quotation.update_layout(
                showlegend=False,
                xaxis_title="Quotation Version Code",
                yaxis_title="Product Quantity"
            )

            # Display
            st.plotly_chart(fig_quotation)

            # st.subheader("👨‍💼 Created By Analysis")
            # created_by_summary = df.groupby('user_name')['product_total_price'].sum().reset_index()
            # fig_user = px.bar(created_by_summary, x='user_name', y='product_total_price',
            #                   title="Quotation Value by Creator", color='user_name')
            # st.plotly_chart(fig_user)

            # Salesperson-wise performance
            st.subheader("🧑‍💼 Salesperson Performance")
            salesperson_perf = df.groupby("user_name").agg({
                "product_quantity": "sum",
                "estimated_total_price": "sum"
            }).reset_index()
            fig3 = px.bar(salesperson_perf, x="user_name", y="estimated_total_price",
                          title="Revenue by Salesperson", labels={"estimated_total_price": "Estimated Revenue"})
            st.plotly_chart(fig3, use_container_width=True)

            st.sidebar.header("🔎 Filter Data")
            selected_status = st.sidebar.multiselect("Select Status", options=df['status'].unique(),
                                                     default=df['status'].unique())

            filtered_df = df[df['status'].isin(selected_status)]
            st.subheader("📄 Filtered Records")
            st.dataframe(filtered_df)

        else:
            st.info("system doesn't have any records.")

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