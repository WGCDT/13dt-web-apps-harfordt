import mysql.connector

print(1)
mydb = mysql.connector.connect(
    host="sql12.freemysqlhosting.net",
    user="sql12290054",
    password="EyExJBdPbn",
    database="sql12290054"
)
print(2)
print(mydb)
