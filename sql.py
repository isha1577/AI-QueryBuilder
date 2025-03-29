import sqlite3

connection = sqlite3.connect("company.db")

cursor = connection.cursor()

table_info = """
CREATE TABLE SALES (
    sale_id VARCHAR(255) PRIMARY KEY,
    company_id INT,
    client_id VARCHAR(255),
    employee_id INT,
    amount DECIMAL(10,2),
    date DATE,
    FOREIGN KEY (company_id) REFERENCES company(company_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
"""
cursor.execute(table_info)

# insert records

cursor.execute('''INSERT INTO SALES (sale_id, company_id, client_id, employee_id, amount, date) 
VALUES 
('S1',101, 'CT1', 201, 12000.00, '2024-03-10'),
('S2',102, 'CT2', 202, 25000.00, '2024-03-15');''')

print("the inserted records are")

data = cursor.execute('''select * from SALES''')

for row in data:
    print(row)

connection.commit()
connection.close()
