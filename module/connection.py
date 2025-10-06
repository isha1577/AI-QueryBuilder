import pandas as pd
from sqlalchemy import create_engine, text

username = "dev_ds_admin"
password = "Nm7mIVc8OHxBv7WoIpo2"
host = "dev-ds-abner-db.cn6koiyu8tn5.ap-south-1.rds.amazonaws.com"
port = 3306
database = "abner_erp_dev"

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")


# ✅ Get credentials from user table
def get_credentials():
    query = "SELECT FIRST_NAME, USER_NAME, PASSWORD FROM user"
    with engine.connect() as conn:
        rows = conn.execute(text(query)).fetchall()

    credentials = {"usernames": {}}
    for FIRST_NAME, USER_NAME, PASSWORD in rows:
        credentials["usernames"][USER_NAME] = {
            "name": FIRST_NAME,
            "password": PASSWORD
        }
    return credentials


# ✅ Fetch suggestions from poc_dashboard
def fetch_suggestions(input_val):
    query = "SELECT questions FROM poc_dashboard WHERE questions LIKE :val LIMIT 10"
    with engine.connect() as conn:
        results = conn.execute(text(query), {"val": f"%{input_val}%"}).fetchall()
    return [item[0] for item in results]


# ✅ Insert or increment question
def insert_or_increment_question(question):
    with engine.begin() as conn:  # begin ensures commit/rollback
        check_query = "SELECT id, count FROM poc_dashboard WHERE questions = :q AND delete_flag = 0"
        result = conn.execute(text(check_query), {"q": question}).fetchone()

        if result:
            faq_id, current_count = result
            update_query = "UPDATE poc_dashboard SET count = :cnt WHERE id = :id AND delete_flag = 0"
            conn.execute(text(update_query), {"cnt": current_count + 1, "id": faq_id})
        else:
            insert_query = "INSERT INTO poc_dashboard (questions, favorite, count) VALUES (:q, :fav, :cnt)"
            result = conn.execute(text(insert_query), {"q": question, "fav": False, "cnt": 1})
            faq_id = result.lastrowid if hasattr(result, "lastrowid") else None
    return faq_id


# ✅ Fetch favorites
def fetch_fav():
    query = "SELECT * FROM poc_dashboard WHERE delete_flag = 0 ORDER BY count DESC"
    with engine.connect() as conn:
        faqs = conn.execute(text(query)).mappings().all()
    return [dict(row) for row in faqs]


# ✅ Update favorite
def update_fav(faq_id, favorite):
    query = "UPDATE poc_dashboard SET favorite = :fav WHERE id = :id AND delete_flag = 0"
    with engine.begin() as conn:
        conn.execute(text(query), {"fav": favorite, "id": faq_id})


# ✅ Get FAQ id by question
def get_faq_id_by_question(question):
    query = "SELECT id FROM poc_dashboard WHERE questions = :q AND delete_flag = 0"
    with engine.connect() as conn:
        result = conn.execute(text(query), {"q": question}).fetchone()
    return result[0] if result else None

def fetch_data(sql):

    dataframe = pd.read_sql(text(sql), con=engine)
    dataframe.to_csv("temp_df.csv", index=False)
    return dataframe