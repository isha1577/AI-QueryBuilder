import mysql.connector
import pandas as pd
import os


# def get_connection():
#     return mysql.connector.connect(
#         host=os.getenv("DB_HOST", "localhost"),
#         user=os.getenv("DB_USER", "root"),
#         password=os.getenv("DB_PASSWORD", "Renuka@1973"),
#         database=os.getenv("DB_NAME", "amber_solutions"),
#         port=int(os.getenv("DB_PORT", 3306))
#     )
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Renuka@1973",
        database="amber_solutions",
        port=3306
    )


def insert_or_increment_question(question):
    conn = get_connection()
    cursor = conn.cursor()
    check_query = "SELECT id, count FROM poc_dashboard WHERE questions = %s"
    cursor.execute(check_query, (question,))
    result = cursor.fetchone()
    if result:
        faq_id, current_count = result
        update_query = "UPDATE poc_dashboard SET count = %s WHERE id = %s"
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
    query = "SELECT * FROM poc_dashboard ORDER BY count DESC"
    cursor.execute(query)
    faqs = cursor.fetchall()
    cursor.close()
    conn.close()
    return faqs


def update_fav(faq_id, favorite):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE poc_dashboard SET favorite = %s WHERE id = %s"
    cursor.execute(query, (favorite, faq_id))
    conn.commit()
    cursor.close()
    conn.close()


def fetch_data(sql):
    conn = get_connection()
    dataframe = pd.read_sql(sql, conn)
    dataframe.to_csv("temp_df.csv", index=False)
    conn.close()
    return dataframe
