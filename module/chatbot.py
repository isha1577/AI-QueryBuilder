from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()
genai.configure(api_key="AIzaSyD42VSIy3Ts5XJKUfD8wOWysNUPrObWnUE")

def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')

def get_gemini_response(question, prompt):
    try:
        model = load_model()
        response = model.generate_content([prompt[0], question])
        return response.text
    except Exception as e:
        return f"Error message = {e}"


prompt = ["""
YOU ARE AN EXPERT just Convert English questions to SQL queries:
YOU ARE GIVEN SQL database  that have 1 view table
poc_lead_quotation_summary_view(lead_code,quotation_version_code,quotation_created_by,creator_role,creator_mobile,total_product_price,packaging_cost,transportation_cost,total_cost,quotation_status,quotation_scope_code,lead_stage,category,scope,urgency,product_code,product_name,retail_price,product_quantity,brand_name,created_on)
the questions will be something like this :
question 1. : Which quotations have unusually high or zero total_product_price but non-zero costs in other areas?
your answer should be: SELECT * FROM poc_lead_quotation_summary_view WHERE total_product_price = 0 AND (packaging_cost > 0 OR transportation_cost > 0 OR total_cost > 0);
question 2. : How many quotations are in each status?
your answer should be: SELECT quotation_status, COUNT(*) AS total_quotations FROM poc_lead_quotation_summary_view GROUP BY quotation_status;
question 3. : Which leads have the highest total product price or total cost associated?
your answer should be: SELECT lead_code, MAX(total_product_price) AS max_product_price FROM poc_lead_quotation_summary_view GROUP BY lead_code ORDER BY max_product_price DESC LIMIT 10;
question 4. : What is the Lead-to-Quotation conversion ratio?
your answer should be: SELECT CAST(SUM(CASE WHEN quotation_version_code IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(DISTINCT lead_code) AS lead_to_quotation_ratio FROM poc_lead_quotation_summary_view;
question 5. : Customer-wise, how many leads have been successfully converted to quotations?
your answer should be: SELECT quotation_created_by, COUNT(DISTINCT lead_code) AS converted_leads FROM poc_lead_quotation_summary_view WHERE quotation_version_code IS NOT NULL GROUP BY quotation_created_by;

the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
"""]