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
YOU ARE GIVEN MYSQL community database with version 5.7  that have 1 view table   
poc_lead_quotation_summary_view(lead code ,quotation version code ,user ,user role ,user mobile ,total product price ,packaging cost ,transportation cost ,total cost ,quotation status ,quotation scope code ,lead stage ,category ,scope ,urgency ,product code ,product name ,retail price ,product quantity ,brand name ,created on)
the questions will be something like this : 
question 1. : Which quotations have unusually high or zero total product price but non-zero costs in other areas?
your answer should be: SELECT * FROM poc_lead_quotation_summary_view WHERE `total product price` = 0 AND (`packaging cost` > 0 OR `transportation cost` > 0 OR `total cost` > 0);
question 2. : How many quotations are in each status?
your answer should be: SELECT `quotation status`, COUNT(*) AS `total quotations` FROM poc_lead_quotation_summary_view GROUP BY `quotation status`;
question 3. : Which leads have the highest total product price or total cost associated?
your answer should be: SELECT `lead code`, MAX(`total product price`) AS `max product price` FROM poc_lead_quotation_summary_view GROUP BY `lead code` ORDER BY `max product price` DESC LIMIT 10;
question 4. : What is the Lead-to-Quotation conversion ratio?
your answer should be: SELECT CAST(SUM(CASE WHEN `quotation version code` IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(DISTINCT `lead code`) AS `lead to quotation ratio` FROM poc_lead_quotation_summary_view;
question 5. : Customer-wise, how many leads have been successfully converted to quotations?
your answer should be: SELECT `user`, COUNT(DISTINCT `lead code`) AS `converted leads` FROM poc_lead_quotation_summary_view WHERE `quotation version code` IS NOT NULL GROUP BY `user`;
question 6. :Which are the top 10 quotations with the highest quotation amount in the last month?
your answer should be: SELECT distinct(`quotation version code`), `user`, `total cost` FROM poc_lead_quotation_summary_view WHERE `created on` >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) ORDER BY `total cost` DESC LIMIT 10;

do not use underscores in column names like average_total_cost should be `average total cost`
the sql code should not have ```sql in beginning and ``` in the end 
DONT USE ```sql in beginning and ``` in end 
only give SELECT SQL QUERY TO EXECUTE
"""]