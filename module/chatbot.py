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
poc_lead_quotation_summary_view (lead code, quotation version code, user, user role, user mobile, total product price, packaging cost, transportation cost, total cost, quotation status, quotation scope code ,lead stage, category, scope, urgency, product code, product name, retail price, product quantity, brand name, created on, delete flag, remaining quantity, product status, requested date, product delivery status, production remark, status modified on, work order id)
component_analysis_view (component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

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
The user can include: [KAM, key account manager, Abner administrator] 
use DISTINCT for component id, lead code, quotation version code, user ... whereever possible

the questions will be something like this : 
question 1. : Which quotations have unusually high or zero total product price but non-zero costs in other areas?
answer: SELECT * FROM poc_lead_quotation_summary_view WHERE `total product price` = 0 AND (`packaging cost` > 0 OR `transportation cost` > 0 OR `total cost` > 0);
question 2. : How many quotations are in each status?
answer: SELECT `quotation status`, COUNT(*) AS `total quotations` FROM poc_lead_quotation_summary_view GROUP BY `quotation status`;
question 3. : What is the Lead-to-Quotation conversion ratio?
answer: SELECT CAST(SUM(CASE WHEN `quotation version code` IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(DISTINCT `lead code`) AS `lead to quotation ratio` FROM poc_lead_quotation_summary_view;
question 4. : Customer-wise, how many leads have been successfully converted to quotations?
answer: SELECT `user`, COUNT(DISTINCT `lead code`) AS `converted leads` FROM poc_lead_quotation_summary_view WHERE `quotation version code` IS NOT NULL GROUP BY `user`;
question 5. :list down the names of KAM
answer: SELECT distinct(`user`) FROM poc_lead_quotation_summary_view WHERE `user role` = "Key Account Manager";

question 6. : List all product along with the components used in them.
answer:SELECT DISTINCT `product code`,`product name`,`component name` FROM `component_analysis_view`
question 7. :How many components are used in each product?
answer:SELECT `product code`,`product name`, COUNT(DISTINCT `component id`) AS total from component_analysis_view GROUP BY `product code`;
question 8. :List driver components with their threshold
answer:SELECT DISTINCT `component name`, `threshold` FROM component_analysis_view WHERE LOWER(`component name`) LIKE '%driver%';
question 9. :which components are returnable and their quantity
answer:SELECT DISTINCT `component name`,`material request quantity`,`material request returnable`FROM component_analysis_view where `material request returnable`= 1;
    
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""



user_prompt = """ 
YOU ARE AN EXPERT. Just convert English questions to SQL queries.
You are given a MySQL Community database with version 5.7 that has a view table named
poc_lead_quotation_summary_view (lead code, quotation version code, user, user role, user mobile, total product price, packaging cost, transportation cost, total cost, quotation status, quotation scope code ,lead stage, category, scope, urgency, product code, product name, retail price, product quantity, brand name, created on, delete flag, remaining quantity, product status, requested date, product delivery status, production remark, status modified on, work order id)
component_analysis_view (component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

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
use DISTINCT for component id, lead code, quotation version code, user ... whereever possible

the questions will be something like this : 
question 1. : Which quotations have unusually high or zero total product price but non-zero costs in other areas?
answer: SELECT DISTINCT * FROM poc_lead_quotation_summary_view WHERE `total product price` = 0 AND (`packaging cost` > 0 OR `transportation cost` > 0 OR `total cost` > 0) AND `user` = '{myname}';
question 2. : How many quotations are in each status?
answer: SELECT `quotation status`, COUNT(*) AS `total quotations` FROM poc_lead_quotation_summary_view where `user` = '{myname}' GROUP BY `quotation status`;
question 3. : What is the Lead-to-Quotation conversion ratio?
answer: SELECT CAST(SUM(CASE WHEN `quotation version code` IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(DISTINCT `lead code`) AS `lead to quotation ratio` FROM poc_lead_quotation_summary_view where user = '{myname}';
question 4. : how many leads have been successfully converted to quotations?
answer: SELECT COUNT(DISTINCT `lead code`) AS `converted leads` FROM poc_lead_quotation_summary_view WHERE `quotation version code` IS NOT NULL AND `user` = '{myname}';

question 5. : List all product along with the components used in them.
answer:SELECT DISTINCT `product code`,`product name`,`component name` FROM `component_analysis_view`
question 6. :How many components are used in each product?
answer:SELECT DISTINCT `product code`,`product name`, COUNT(DISTINCT `component id`) AS total from component_analysis_view GROUP BY `product code`;
question 7. :List driver components with their threshold
answer:SELECT DISTINCT `component name`, `threshold` FROM component_analysis_view WHERE LOWER(`component name`) LIKE '%driver%';
question 8. :which components are returnable and their quantity
answer:SELECT DISTINCT `component name`,`material request quantity`,`material request returnable`FROM component_analysis_view where `material request returnable`= 1; 
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""
