import sqlite3

connection = sqlite3.connect("company.db")

cursor = connection.cursor()

# table_info = """
# CREATE TABLE SALES (
#     sale_id VARCHAR(255) PRIMARY KEY,
#     company_id INT,
#     client_id VARCHAR(255),
#     employee_id INT,
#     amount DECIMAL(10,2),
#     date DATE,
#     FOREIGN KEY (company_id) REFERENCES co    mpany(company_id),
#     FOREIGN KEY (client_id) REFERENCES clients(client_id),
#     FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
# );
# """
# cursor.execute(table_info)

# insert records

# cursor.execute('''INSERT INTO SALES (sale_id, company_id, client_id, employee_id, amount, date)
# VALUES
# ('S3',101, 'CT1', 201, 10000.00, '2024-04-10'),
# ('S4',102, 'CT2', 202, 20000.00, '2024-04-15'),
# ('S5',101, 'CT1', 201, 32000.00, '2024-04-16'),
# ('S6',102, 'CT2', 202, 45000.00, '2024-05-13');''')

print("the inserted records are")

data = cursor.execute('''select * from PROJECTS''')

for row in data:
    print(row)

connection.commit()
connection.close()
