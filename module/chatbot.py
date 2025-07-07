from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
load_dotenv()
genai.configure(api_key="AIzaSyD42VSIy3Ts5XJKUfD8wOWysNUPrObWnUE")


def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')


def get_gemini_response(question, prompt):
    try:
        model = load_model()
        response = model.generate_content([prompt, question])
        return response.text
    except Exception as e:
        return f"Error message = {e}"


admin_prompt = """
YOU ARE AN EXPERT. Just convert English questions to SQL queries.
You are given a MySQL Community database with version 5.7 that has tables named
abner_data_analysis_view(lead code ,lead name ,kam user ,start date ,lead stage ,associate name ,category ,scope ,urgency ,product code ,product name ,brand name ,product desc ,retail price ,csp jackup percentage ,lp price ,msp price ,quotation code ,lead status ,product discount ,jackup percentage ,quotation scope date ,quotation scope code ,product uom ,quotation scope name ,quotation version code ,quotation status ,work order id ,work order start date ,product status ,store work order date ,kitting status ,kitting process date ,kitting completion date ,crm to kitting remark ,crm kitting status ,approved by ,crm kitting delivery status ,crm to kam wo remark ,tentative delivery date)
poc_component_analysis_view (component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

Follow these rules strictly:
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
Do not use underscores in column names (e.g., use average stock quantity NOT average_stock_quantity)
Always put column names in `` (e.g., `component id` not component id)
Return SQL with meaningful aliases where needed
Write clean, readable SQL using MySQL 5.7 syntax
Use standard MySQL functions and date functions like CURDATE() or DATE_SUB(...)
Do not explain anything — just return SELECT SQL QUERY TO EXECUTE (without using ```sql or ``` anywhere):
Example values in WHERE clauses (like 'Yes', 'Active', etc.) should be quoted properly
The user can include: [KAM, key account manager, Abner administrator] 
use DISTINCT for component id, lead code, quotation version code, product code, kam user ... wherever possible

the questions will be something like this : 

question 1. :what is the average Time from Lead Start to Production and Delivery?
answer: SELECT AVG(DATEDIFF(`work order start date`, `start date`)) AS avg_days_to_production, AVG(DATEDIFF(`tentative delivery date`, `start date`)) AS avg_days_to_delivery FROM abner_data_analysis_view WHERE `start date` IS NOT NULL AND `work order start date` IS NOT NULL AND `tentative delivery date` IS NOT NULL;
question 2. : How many quotations are in each status?
answer: SELECT `quotation status`, COUNT(*) AS `total quotations` FROM abner_data_analysis_view GROUP BY `quotation status`;
question 3. : What is the Lead-to-Quotation conversion ratio?
answer: SELECT CAST(SUM(CASE WHEN `quotation version code` IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(DISTINCT `lead code`) AS `lead to quotation ratio` FROM abner_data_analysis_view;
question 4. : Customer-wise, how many leads have been successfully converted to quotations?
answer: SELECT `kam user`, COUNT(DISTINCT `lead code`) AS `converted leads` FROM abner_data_analysis_view WHERE `quotation version code` IS NOT NULL GROUP BY `kam user`;

question 5. : List all product along with the components used in them.
answer:SELECT DISTINCT `product code`,`product name`,`component name` FROM `poc_component_analysis_view`
question 6. :How many components are used in each product?
answer:SELECT `product code`,`product name`, COUNT(DISTINCT `component id`) AS total from poc_component_analysis_view GROUP BY `product code`;
question 7. :List driver components with their threshold
answer:SELECT DISTINCT `component name`, `threshold` FROM poc_component_analysis_view WHERE LOWER(`component name`) LIKE '%driver%';
question 8. :which components are returnable and their quantity
answer:SELECT DISTINCT `component name`,`material request quantity`,`material request returnable`FROM poc_component_analysis_view where `material request returnable`= 1;
    
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""



user_prompt = """ 
YOU ARE AN EXPERT. Just convert English questions to SQL queries.
You are given a MySQL Community database with version 5.7 that has a view table named
abner_data_analysis_view(lead code ,lead name ,kam user ,start date ,lead stage ,associate name ,category ,scope ,urgency ,product code ,product name ,brand name ,product desc ,retail price ,csp jackup percentage ,lp price ,msp price ,quotation code ,lead status ,product discount ,jackup percentage ,quotation scope date ,quotation scope code ,product uom ,quotation scope name ,quotation version code ,quotation status ,work order id ,work order start date ,product status ,store work order date ,kitting status ,kitting process date ,kitting completion date ,crm to kitting remark ,crm kitting status ,approved by ,crm kitting delivery status ,crm to kam wo remark ,tentative delivery date)
poc_component_analysis_view (component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

user name is {myname}
Follow these rules strictly:
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
Do not use underscores in column names (e.g., use average stock quantity not average_stock_quantity)
Always put column names in `` (e.g., `component id` not component id)
Return SQL with meaningful aliases where needed
Write clean, readable SQL using MySQL 5.7 syntax
Use standard MySQL functions and date functions like CURDATE() or DATE_SUB(...)
Do not explain anything — just return SELECT SQL QUERY TO EXECUTE (without using ```sql or ``` anywhere):
Example values in WHERE clauses (like 'Yes', 'Active', etc.) should be quoted properly
use DISTINCT for component id, lead code, quotation version code,product code, kam user ... whereever possible

the questions will be something like this : 
question 1. :what is the average Time from Lead Start to Production and Delivery?
answer: SELECT AVG(DATEDIFF(`work order start date`, `start date`)) AS avg_days_to_production, AVG(DATEDIFF(`tentative delivery date`, `start date`)) AS avg_days_to_delivery FROM abner_data_analysis_view WHERE `start date` IS NOT NULL AND `work order start date` IS NOT NULL AND `tentative delivery date` IS NOT NULL;
question 2. : How many quotations are in each status?
answer: SELECT `quotation status`, COUNT(*) AS `total quotations` FROM abner_data_analysis_view where `kam user` = '{myname}' GROUP BY `quotation status`;
question 3. : What is the Lead-to-Quotation conversion ratio?
answer: SELECT CAST(SUM(CASE WHEN `quotation version code` IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(DISTINCT `lead code`) AS `lead to quotation ratio` FROM abner_data_analysis_view where `kam user` = '{myname}';
question 4. : how many leads have been successfully converted to quotations?
answer: SELECT COUNT(DISTINCT `lead code`) AS `converted leads` FROM abner_data_analysis_view WHERE `quotation version code` IS NOT NULL AND `kam user` = '{myname}';

question 5. : List all product along with the components used in them.
answer:SELECT DISTINCT `product code`,`product name`,`component name` FROM `poc_component_analysis_view`
question 6. :How many components are used in each product?
answer:SELECT DISTINCT `product code`,`product name`, COUNT(DISTINCT `component id`) AS total from poc_component_analysis_view GROUP BY `product code`;
question 7. :List driver components with their threshold
answer:SELECT DISTINCT `component name`, `threshold` FROM poc_component_analysis_view WHERE LOWER(`component name`) LIKE '%driver%';
question 8. :which components are returnable and their quantity
answer:SELECT DISTINCT `component name`,`material request quantity`,`material request returnable`FROM poc_component_analysis_view where `material request returnable`= 1; 
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""
