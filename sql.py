import sqlite3

connection = sqlite3.connect("student.db")

cursor = connection.cursor()

table_info ="""
Create table TEACHERS(Name VARCHAR(25),CLASS VARCHAR(25),
TECID VARCHAR(25)
);
"""
cursor.execute(table_info)


# insert records 

cursor.execute('''INSERT INTO TEACHERS VALUES ('Aman', 'Cyber Security', 'T32')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Priya', 'Mathematics', 'T45')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Raj', 'Physics', 'T12')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Sita', 'Chemistry', 'T67')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Vikram', 'Computer Science', 'T89')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Neha', 'Electrical Engineering', 'T23')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Karan', 'Mechanical Engineering', 'T56')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Anjali', 'Artificial Intelligence', 'T78')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Ravi', 'Biotechnology', 'T91')''')
cursor.execute('''INSERT INTO TEACHERS VALUES ('Sunita', 'Economics', 'T34')''')


print("the inserted records are")

data =cursor.execute('''select * from STUDENT''')

for row in data:
    print(row)
    
    
connection.commit()
connection.close()