import mysql.connector


connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=input("Enter MySQL password: "),
    database="smart_hospital"
)


if connection.is_connected():

    print("SUCCESS!")
    print("Python is connected to MySQL.")
    print("Database: smart_hospital")


connection.close()

print("Connection closed.")