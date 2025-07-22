import mysql.connector
import pandas as pd
import os
from sqlalchemy import create_engine, text

username = "dev_ds_admin"
# Encode special characters in the password
password = "Nm7mIVc8OHxBv7WoIpo2"
host = "dev-ds-abner-db.cn6koiyu8tn5.ap-south-1.rds.amazonaws.com"
port = 3306
database = "dev-ds-abner-db"

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")


def get_connection():
    return mysql.connector.connect(
    host="dev-ds-abner-db.cn6koiyu8tn5.ap-south-1.rds.amazonaws.com",
    user="dev_ds_admin",
    password="Nm7mIVc8OHxBv7WoIpo2",
    database="dev-ds-abner-db",
    port=3306
)

def get_credentials():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT FIRST_NAME, USER_NAME, PASSWORD FROM user")
    rows = cursor.fetchall()
    conn.close()

    credentials = {"usernames": {}}
    for FIRST_NAME, USER_NAME, PASSWORD in rows:
        credentials["usernames"][USER_NAME] = {
            "name": FIRST_NAME,
            "password": PASSWORD
        }
    return credentials

def fetch_suggestions(input_val):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT questions FROM poc_dashboard WHERE questions LIKE %s LIMIT 10"
    cursor.execute(query, ('%' + input_val + '%',))
    results = [item[0] for item in cursor.fetchall()]
    cursor.close()
    conn.close()
    return results


def insert_or_increment_question(question):
    conn = get_connection()
    cursor = conn.cursor()
    check_query = "SELECT id, count FROM poc_dashboard WHERE questions = %s and delete_flag = 0"
    cursor.execute(check_query, (question,))
    result = cursor.fetchone()
    if result:
        faq_id, current_count = result
        update_query = "UPDATE poc_dashboard SET count = %s WHERE id = %s and delete_flag = 0"
        cursor.execute(update_query, (current_count + 1, faq_id))
    else:
        insert_query = "INSERT INTO poc_dashboard (questions, favorite, count) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (question, False, 1))
        faq_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return faq_id


def fetch_fav():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM poc_dashboard where delete_flag = 0 ORDER BY count DESC"
    cursor.execute(query)
    faqs = cursor.fetchall()
    cursor.close()
    conn.close()
    return faqs


def update_fav(faq_id, favorite):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE poc_dashboard SET favorite = %s WHERE id = %s and delete_flag = 0"
    cursor.execute(query, (favorite, faq_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_faq_id_by_question(question):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id FROM poc_dashboard WHERE questions = %s and delete_flag = 0"
    cursor.execute(query, (question,))
    result = cursor.fetchone()
    faq_id = result[0] if result else None
    cursor.close()
    conn.close()
    return faq_id

def fetch_data(sql):

    dataframe = pd.read_sql(text(sql), con=engine)
    dataframe.to_csv("temp_df.csv", index=False)
    return dataframe