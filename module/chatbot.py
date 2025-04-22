from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()
genai.configure(api_key="AIzaSyCyRuwrNy_-MF70zVllAQakriq7T5FuyM0")

def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')

def get_gemini_response(question, prompt):
    model = load_model()
    response = model.generate_content([prompt[0], question])
    return response.text

prompt = ["""
YOU ARE AN EXPERT just Convert English questions to SQL queries:
YOU ARE GIVEN SQL database  that have 2 view tables 
poc_lead_quotation_summary_view(lead_code, quotation_version_code, quotation_created_by, creator_role, creator_mobile, total_product_price, packaging_cost, transportation_cost, total_cost, quotation_status, quotation_scope_code, lead_stage, category, scope, urgency)

the questions will be something like this :
question 1. : Which quotations have unusually high or zero total_product_price but non-zero costs in other areas?
your answer should be: SELECT * FROM poc_lead_quotation_summary_view WHERE total_product_price = 0 AND (packaging_cost > 0 OR transportation_cost > 0 OR total_cost > 0);
question 2. : How many quotations are in each status?
your answer should be: SELECT quotation_status, COUNT(*) AS total_quotations FROM poc_lead_quotation_summary_view GROUP BY quotation_status;
question 3. : Which leads have the highest total product price or total cost associated?
your answer should be: SELECT lead_code, MAX(total_product_price) AS max_product_price FROM poc_lead_quotation_summary_view GROUP BY lead_code ORDER BY max_product_price DESC LIMIT 10;

the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
"""]