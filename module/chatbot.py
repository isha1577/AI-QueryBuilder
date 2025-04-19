from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()
genai.configure(api_key="AIzaSyC2ihGO4LEFAJ_FVuZrKgtGOEbu0bEFo7U")

def load_model():
    return genai.GenerativeModel('models/gemini-1.5-pro-latest')

def get_gemini_response(question, prompt):
    model = load_model()
    response = model.generate_content([prompt[0], question])
    return response.text

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