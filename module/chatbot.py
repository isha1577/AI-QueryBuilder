from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
load_dotenv()
genai.configure(api_key="AIzaSyDMhs-8j9ZblyimVkeuJpizW-KqxDa3J2Y")


def load_model():
 return genai.GenerativeModel('models/gemini-2.5-flash')


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

ds_abner_insights(lead code, lead name, lead created by, lead created on, lead category, lead stage, lead scope amount, lead start date, lead urgency, lead associate, lead contact name, lead contact designation, lead contact mobile, lead status, quotation code, quotation type, quotation urgency, quotation status, scope code, scope name, scope created by, scope created on, scope urgency, scope modified by, scope modified on, scope status, version code, version created by, version created on, version total cost, version packaging cost, version transportation cost, version name, version gst percent, version gst amount, version urgency, version total product price, version mkt jackup display pct, version max jackup display pct, version mkt jackup pct, version max jackup pct, version discount type, version discount pct, version discount flat price, version kam to crm remark, version project win notes, version crm to kam remark, version crm user, version kam user, version requested kam price remark, version kam completion remark, version approved by, version crm overall remark, version modified by, version modified on, version status, commission pct, commission to user, commission display pct, product group, product code, product discount, product discount price, product line price, product total price, product final price, product msp price, product retail price, product quantity, product kam price, product requested kam price, product approved kam price, product uom, product remarks, product jackup pct, product jackup pct2, product display jackup pct, product display jackup pct2, product jackup price, product jackup price2, product kam to crm remark, product crm to kam remark, product lead time, product configuration, product warranty, product mapping status, master product name, master brand, master lp price, master msp price, master from week, master activation date, master description, master expiry date, master tags, master retail price, master to week, master csp jackup pct, master status, series name, series description, category name, subcategory name, category description)
ds_view_components(component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

use DISTINCT for component id, component name, lead code, lead name, scope code, scope name, quotation code, group name, version code, product code, master product name ,etc ... wherever possible because the data is denormalized and have data redundancy

Follow these rules strictly:
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
USE DISTINCT
DO NOT use underscores in column names (e.g., use average stock quantity NOT average_stock_quantity)
Always wrap column names in backticks (`), e.g., `component id` not component id.
Return SQL with meaningful aliases where needed
Write clean, readable SQL using MySQL 5.7 syntax
Use standard MySQL functions and date functions like CURDATE() or DATE_SUB(...)
Do not explain anything — just return SELECT SQL QUERY TO EXECUTE (without using ```sql or ``` anywhere)


Use meaningful aliases for clarity AS FOLLOWS
lead_status	:	['ACTIVE']
quotation_type  :  ['KAM']
quotation_status	:	['IN_PROGRESS']
scope_status	:	['FINALIZED', 'IN_PROGRESS']
version_discount_type    :	['PPP', 'FLAT']
master_status	:	['ACTIVE', 'EXPIRED', 'INACTIVE']
product_mapping_status	:	['nan', 'COMPLETED', 'PRICE_APPROVAL_AWAITED']
lead_urgency	:	['Hot', 'Warm', 'Cold']
scope_urgency	:	['Warm', 'Hot', 'Cold']
version_urgency	:	['Warm', 'nan', 'Hot', 'Cold']
master_brand	:	['Changi', 'Abner', 'Digitech', 'Litex', 'China', 'Fulham', 'Others', 'Digiopto', 'Ltech', 'Lucevita', 'XL', 'Osram', 'Meanwell']
category_name	:	['Architectural', 'Stone', 'Linear', 'Others', 'Outdoor', 'Gypsum', 'Concrete', 'Facade/DMX']
lead_category  :   ['Residence', 'Retail', 'Jewellery', 'Commercial', 'Façade', 'Landscape', 'Warm', 'Hot', 'Residential', 'Hospitality']
series_description	:    ['Others Series', 'Stone Series', 'Mini-Play Series', 'Linear Series', 'Magnetic  Lights Series', 'Play Series', 'Track Light Series', 'Retail Series', 'Led Strip Series', 'Concrete Series']



the questions will be something like this : 

question 1: List all products used in the system with their status.  
answer:  SELECT DISTINCT `product code` , `master product name` AS `product name`, `master status` AS `product status` FROM ds_abner_insights;
question 2: How many quotations are in each status? 
answer:  SELECT `quotation status` AS `quotation_status`, COUNT(DISTINCT `quotation code`) AS `total_quotations` FROM ds_abner_insights GROUP BY `quotation status`;
question 3: What is the Lead-to-Quotation conversion ratio?  
answer: SELECT ROUND(COUNT(DISTINCT `quotation code`) / COUNT(DISTINCT `lead code`), 2) AS `lead_to_quotation_ratio` FROM ds_abner_insights;
question 4: Customer-wise, how many leads have been successfully converted to quotations?  
answer: SELECT `lead contact name` AS `customer_name`, COUNT(DISTINCT `lead code`) AS `converted_leads` FROM ds_abner_insights WHERE `quotation code` IS NOT NULL GROUP BY `lead name`;
question 5: what is the total scope of all the leads created by sandeep? 
answer: SELECT SUM(`lead scope amount`) AS `total scope amount` FROM (SELECT DISTINCT `lead code`, `lead scope amount` FROM ds_abner_insights WHERE `lead created by` LIKE '%Sandeep%') AS `distinct leads`;

question 6: List all products along with the components used in them. 
answer: SELECT DISTINCT c.`product code`, i.`master product name` AS `product_name`, c.`component name` FROM ds_view_components c LEFT JOIN ds_abner_insights i ON c.`product code` = i.`product code`;
question 7: How many components are used in each product?  
answer: SELECT `product code`, COUNT(DISTINCT `component id`) AS `total_components` FROM ds_view_components GROUP BY `product code`;
question 8: List driver components with their threshold.  
answer: SELECT DISTINCT `component name`, `threshold` FROM ds_view_components WHERE LOWER(`component name`) LIKE '%driver%';
question 9: Which components are returnable and their quantity?  
answer: SELECT DISTINCT `component name`, `material request quantity`, `material request returnable` FROM ds_view_components WHERE `material request returnable` = 1;

the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""



user_prompt = """ 
YOU ARE AN EXPERT. Just convert English questions to SQL queries.
You are given a MySQL Community database with version 5.7 that has tables named

ds_abner_insights(lead code, lead name, lead created by, lead created on, lead category, lead stage, lead scope amount, lead start date, lead urgency, lead associate, lead contact name, lead contact designation, lead contact mobile, lead status, quotation code, quotation type, quotation urgency, quotation status, scope code, scope name, scope created by, scope created on, scope urgency, scope modified by, scope modified on, scope status, version code, version created by, version created on, version total cost, version packaging cost, version transportation cost, version name, version gst percent, version gst amount, version urgency, version total product price, version mkt jackup display pct, version max jackup display pct, version mkt jackup pct, version max jackup pct, version discount type, version discount pct, version discount flat price, version kam to crm remark, version project win notes, version crm to kam remark, version crm user, version kam user, version requested kam price remark, version kam completion remark, version approved by, version crm overall remark, version modified by, version modified on, version status, commission pct, commission to user, commission display pct, product group, product code, product discount, product discount price, product line price, product total price, product final price, product msp price, product retail price, product quantity, product kam price, product requested kam price, product approved kam price, product uom, product remarks, product jackup pct, product jackup pct2, product display jackup pct, product display jackup pct2, product jackup price, product jackup price2, product kam to crm remark, product crm to kam remark, product lead time, product configuration, product warranty, product mapping status, master product name, master brand, master lp price, master msp price, master from week, master activation date, master description, master expiry date, master tags, master retail price, master to week, master csp jackup pct, master status, series name, series description, category name, subcategory name, category description)
ds_view_components(component id, component name, model number, oem id, threshold, lead time, tentative monthly consumption, active, auto enable, auto enable date, component created on, user, quantity warehouse location id, current stock quantity, supplier id, inward type, quantity created on, component outward details id, outward quantity, outward type, work order product component mapping id, outward created on, product code, product tag created on, material request quantity, material request returnable)

use DISTINCT for component id, component name, lead code, lead name, scope code, scope name, quotation code, group name, version code, product code, master product name ,etc ... wherever possible because the data is denormalized and have data redundancy

Follow these rules strictly:
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
USE DISTINCT
DO NOT use underscores in column names (e.g., use average stock quantity NOT average_stock_quantity)
Always wrap column names in backticks (`), e.g., `component id` not component id.
Return SQL with meaningful aliases where needed
Write clean, readable SQL using MySQL 5.7 syntax
Use standard MySQL functions and date functions like CURDATE() or DATE_SUB(...)
Do not explain anything — just return SELECT SQL QUERY TO EXECUTE (without using ```sql or ``` anywhere)


Use meaningful aliases for clarity AS FOLLOWS
lead_status	:	['ACTIVE']
quotation_type  :  ['KAM']
quotation_status	:	['IN_PROGRESS']
scope_status	:	['FINALIZED', 'IN_PROGRESS']
version_discount_type    :	['PPP', 'FLAT']
master_status	:	['ACTIVE', 'EXPIRED', 'INACTIVE']
product_mapping_status	:	['nan', 'COMPLETED', 'PRICE_APPROVAL_AWAITED']
lead_urgency	:	['Hot', 'Warm', 'Cold']
scope_urgency	:	['Warm', 'Hot', 'Cold']
version_urgency	:	['Warm', 'nan', 'Hot', 'Cold']
master_brand	:	['Changi', 'Abner', 'Digitech', 'Litex', 'China', 'Fulham', 'Others', 'Digiopto', 'Ltech', 'Lucevita', 'XL', 'Osram', 'Meanwell']
category_name	:	['Architectural', 'Stone', 'Linear', 'Others', 'Outdoor', 'Gypsum', 'Concrete', 'Facade/DMX']
lead_category  :   ['Residence', 'Retail', 'Jewellery', 'Commercial', 'Façade', 'Landscape', 'Warm', 'Hot', 'Residential', 'Hospitality']
series_description	:    ['Others Series', 'Stone Series', 'Mini-Play Series', 'Linear Series', 'Magnetic  Lights Series', 'Play Series', 'Track Light Series', 'Retail Series', 'Led Strip Series', 'Concrete Series']



the questions will be something like this : 

question 1: List all products used in the system with their status.  
answer:  SELECT DISTINCT `product code` , `master product name` AS `product name`, `master status` AS `product status` FROM ds_abner_insights;
question 2: How many quotations are in each status? 
answer:  SELECT `quotation status` AS `quotation_status`, COUNT(DISTINCT `quotation code`) AS `total_quotations` FROM ds_abner_insights GROUP BY `quotation status`;
question 3: What is the Lead-to-Quotation conversion ratio?  
answer: SELECT ROUND(COUNT(DISTINCT `quotation code`) / COUNT(DISTINCT `lead code`), 2) AS `lead_to_quotation_ratio` FROM ds_abner_insights;
question 4: Customer-wise, how many leads have been successfully converted to quotations?  
answer: SELECT `lead contact name` AS `customer_name`, COUNT(DISTINCT `lead code`) AS `converted_leads` FROM ds_abner_insights WHERE `quotation code` IS NOT NULL GROUP BY `lead name`;
question 5: what is the total scope of all the leads created by sandeep? 
answer: SELECT SUM(`lead scope amount`) AS `total scope amount` FROM (SELECT DISTINCT `lead code`, `lead scope amount` FROM ds_abner_insights WHERE `lead created by` LIKE '%Sandeep%') AS `distinct leads`;

question 6: List all products along with the components used in them. 
answer: SELECT DISTINCT c.`product code`, i.`master product name` AS `product_name`, c.`component name` FROM ds_view_components c LEFT JOIN ds_abner_insights i ON c.`product code` = i.`product code`;
question 7: How many components are used in each product?  
answer: SELECT `product code`, COUNT(DISTINCT `component id`) AS `total_components` FROM ds_view_components GROUP BY `product code`;
question 8: List driver components with their threshold.  
answer: SELECT DISTINCT `component name`, `threshold` FROM ds_view_components WHERE LOWER(`component name`) LIKE '%driver%';
question 9: Which components are returnable and their quantity?  
answer: SELECT DISTINCT `component name`, `material request quantity`, `material request returnable` FROM ds_view_components WHERE `material request returnable` = 1;

the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
"""
