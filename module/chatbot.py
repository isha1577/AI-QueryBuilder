from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
load_dotenv()
genai.configure(api_key="AIzaSyDd1r_-qpi8k821zKwIwQpO4RiaXQdUmTY")


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
ds_view_lead_quotation_product(lt lead id, lt created by, lt created on, lt category, lt client name, lt lead code, lt lead stage, lt scope, lt start date, lt status, lt urgency, lt lead name, u user name, u role code, u first name, u emp id, u user type, u warehouse location id, q quotation id, q lead code, q quotation code, q quotation type, q status, q urgency, qs quotation scope id, qs created by, qs created on, qs modified by,qs packaging cost, qs quotation code, qs quotation id, qs quotation scope code, qs quotation scope name, qs status, qs transportation cost, qs urgency, qs tnc, qv quotation version id, qv created by, qv created on, qv modified on, qv quotation scope code, qv quotation scope id, qv quotation version code, qv remarks, qv status, qv total cost, qv packaging cost, qv transportation cost, qv version name, qv gst, qv gst amount, qv urgency, qv total product price, qv quotation code, qv quotation version display code, qv kam to crm version remark, qv crm to kam version remark, qv crm user, qv kam user, qv marketing total jackup display percentage, qv version max jackup display percentage, qv product requested kam price remark, qv approved by, qv marketing total jackup percentage, qv version max jackup percentage, qv version discount type, qv version discount percentage, qv version discount flat price, qv CRM overall remark, qv kam completion remark, qvc commission id, qvc commission percent, qvc commission to, qvc quotation version code, qvc quotation version id, qvc commission display percent, qvpm qv product mapping id, qvpm group name, qvpm product code, qvpm product discount, qvpm product discount price, qvpm product line price, qvpm product quantity, qvpm product uom, qvpm quotation version code, qvpm quotation version id, qvpm product total price, qvpm jackup percentage, qvpm jackup price, qvpm product final price, qvpm product msp price, qvpm product remarks, qvpm product retail price, qvpm jackup percentage 2, qvpm jackup price 2, qvpm product warranty, qvpm kam to crm remark, qvpm crm to kam remark, qvpm lead time, qvpm product configuration, qvpm display jackup percentage, qvpm display jackup percentage 2, qvpm product kam price, qvpm product requested kam price, qvpm product approved kam price, qvpm status, pm product id, pm brand name, pm cp code, pm cp only product, pm from week, pm lp price, pm msp price, pm product activation date, pm product category code, pm product code, pm product desc, pm product expiry date, pm product name, pm product series code, pm product sub category code, pm product tags, pm retail price, pm status, pm to week, pm cp price, pm ctc price, pm csp jackup percentage, pm recommended, pm oem id, pm supplier id, pm model number, psm ID, psm NAME, psm CODE, psm DESC, psm SEQUENCE, c ID, c CATEGORY CODE, c CATEGORY NAME, c CATEGORY SEQ, c SUB CATEGORY NAME, c DESCRIPTION)
ds_view_components(component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

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

question 1. :List all products used in the system with their status.
answer: SELECT DISTINCT `pm product_code` AS product_code, `pm product_name` AS product_name, `pm status` AS product_status FROM ds_view_lead_quotation_product;
question 2. : How many quotations are in each status?
answer: SELECT `q status` AS quotation_status, COUNT(DISTINCT `q quotation_code`) AS total_quotations FROM ds_view_lead_quotation_product GROUP BY `q status`;
question 3. : What is the Lead-to-Quotation conversion ratio?
answer: SELECT ROUND(COUNT(DISTINCT `q quotation_code`) / COUNT(DISTINCT `lt lead code`), 2) AS lead_to_quotation_ratio FROM ds_view_lead_quotation_product;
question 4. : Customer-wise, how many leads have been successfully converted to quotations?
answer:SELECT `lt client name` AS customer_name, COUNT(DISTINCT `lt lead code`) AS converted_leads FROM ds_view_lead_quotation_product WHERE `q quotation_code` IS NOT NULL GROUP BY `lt client name`;

question 5. : List all product along with the components used in them.
answer:SELECT DISTINCT `product code`,`product name`,`component name` FROM `ds_view_components`
question 6. :How many components are used in each product?
answer:SELECT `product code`,`product name`, COUNT(DISTINCT `component id`) AS total from ds_view_components GROUP BY `product code`;
question 7. :List driver components with their threshold
answer:SELECT DISTINCT `component name`, `threshold` FROM ds_view_components WHERE LOWER(`component name`) LIKE '%driver%';
question 8. :which components are returnable and their quantity
answer:SELECT DISTINCT `component name`,`material request quantity`,`material request returnable`FROM ds_view_components where `material request returnable`= 1;
 
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""



user_prompt = """ 
YOU ARE AN EXPERT. Just convert English questions to SQL queries.
You are given a MySQL Community database with version 5.7 that has a view table named
ds_view_lead_quotation_product(lt lead id, lt created by, lt created on, lt category, lt client name, lt lead code, lt lead stage, lt scope, lt start date, lt status, lt urgency, lt lead name, u user name, u role code, u first name, u emp id, u user type, u warehouse location id, q quotation id, q lead code, q quotation code, q quotation type, q status, q urgency, qs quotation scope id, qs created by, qs created on, qs modified by,qs packaging cost, qs quotation code, qs quotation id, qs quotation scope code, qs quotation scope name, qs status, qs transportation cost, qs urgency, qs tnc, qv quotation version id, qv created by, qv created on, qv modified on, qv quotation scope code, qv quotation scope id, qv quotation version code, qv remarks, qv status, qv total cost, qv packaging cost, qv transportation cost, qv version name, qv gst, qv gst amount, qv urgency, qv total product price, qv quotation code, qv quotation version display code, qv kam to crm version remark, qv crm to kam version remark, qv crm user, qv kam user, qv marketing total jackup display percentage, qv version max jackup display percentage, qv product requested kam price remark, qv approved by, qv marketing total jackup percentage, qv version max jackup percentage, qv version discount type, qv version discount percentage, qv version discount flat price, qv CRM overall remark, qv kam completion remark, qvc commission id, qvc commission percent, qvc commission to, qvc quotation version code, qvc quotation version id, qvc commission display percent, qvpm qv product mapping id, qvpm group name, qvpm product code, qvpm product discount, qvpm product discount price, qvpm product line price, qvpm product quantity, qvpm product uom, qvpm quotation version code, qvpm quotation version id, qvpm product total price, qvpm jackup percentage, qvpm jackup price, qvpm product final price, qvpm product msp price, qvpm product remarks, qvpm product retail price, qvpm jackup percentage 2, qvpm jackup price 2, qvpm product warranty, qvpm kam to crm remark, qvpm crm to kam remark, qvpm lead time, qvpm product configuration, qvpm display jackup percentage, qvpm display jackup percentage 2, qvpm product kam price, qvpm product requested kam price, qvpm product approved kam price, qvpm status, pm product id, pm brand name, pm cp code, pm cp only product, pm from week, pm lp price, pm msp price, pm product activation date, pm product category code, pm product code, pm product desc, pm product expiry date, pm product name, pm product series code, pm product sub category code, pm product tags, pm retail price, pm status, pm to week, pm cp price, pm ctc price, pm csp jackup percentage, pm recommended, pm oem id, pm supplier id, pm model number, psm ID, psm NAME, psm CODE, psm DESC, psm SEQUENCE, c ID, c CATEGORY CODE, c CATEGORY NAME, c CATEGORY SEQ, c SUB CATEGORY NAME, c DESCRIPTION)
ds_view_components(component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

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
question 1. :List all products used in the system with their status.
answer: SELECT DISTINCT `pm product_code` AS product_code, `pm product_name` AS product_name, `pm status` AS product_status FROM ds_view_lead_quotation_product;
question 2. : How many quotations are in each status?
answer: SELECT `q status` AS quotation_status, COUNT(DISTINCT `q quotation_code`) AS total_quotations FROM ds_view_lead_quotation_product GROUP BY `q status`;
question 3. : What is the Lead-to-Quotation conversion ratio?
answer: SELECT ROUND(COUNT(DISTINCT `q quotation_code`) / COUNT(DISTINCT `lt lead code`), 2) AS lead_to_quotation_ratio FROM ds_view_lead_quotation_product;
question 4. : Customer-wise, how many leads have been successfully converted to quotations?
answer:SELECT `lt client name` AS customer_name, COUNT(DISTINCT `lt lead code`) AS converted_leads FROM ds_view_lead_quotation_product WHERE `q quotation_code` IS NOT NULL GROUP BY `lt client name`;

question 5. : List all product along with the components used in them.
answer:SELECT DISTINCT `product code`,`product name`,`component name` FROM `ds_view_components`
question 6. :How many components are used in each product?
answer:SELECT DISTINCT `product code`,`product name`, COUNT(DISTINCT `component id`) AS total from ds_view_components GROUP BY `product code`;
question 7. :List driver components with their threshold
answer:SELECT DISTINCT `component name`, `threshold` FROM ds_view_components WHERE LOWER(`component name`) LIKE '%driver%';
question 8. :which components are returnable and their quantity
answer:SELECT DISTINCT `component name`,`material request quantity`,`material request returnable`FROM ds_view_components where `material request returnable`= 1; 
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""
