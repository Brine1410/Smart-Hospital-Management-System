import mysql.connector
import streamlit as st
from mysql.connector import Error


st.set_page_config(
    page_title="Smart Hospital Management System",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Smart Hospital Management System")
st.write("Hospital database overview")


st.sidebar.header("Database Connection")

db_password = st.sidebar.text_input(
    "MySQL root password",
    type="password",
)

if not db_password:
    st.info("Enter your MySQL password in the sidebar to continue.")
    st.stop()


connection = None

try:
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=db_password,
        database="smart_hospital",
    )

    cursor = connection.cursor()

    queries = {
        "Patients": "SELECT COUNT(*) FROM patient",
        "Admissions": "SELECT COUNT(*) FROM admission",
        "Prescriptions": "SELECT COUNT(*) FROM prescription",
        "Bills": "SELECT COUNT(*) FROM billing",
    }

    results = {}

    for label, query in queries.items():
        cursor.execute(query)
        results[label] = cursor.fetchone()[0]

    cursor.close()

    st.success("Connected to MySQL successfully.")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Patients", f"{results['Patients']:,}")
    col2.metric("Admissions", f"{results['Admissions']:,}")
    col3.metric("Prescriptions", f"{results['Prescriptions']:,}")
    col4.metric("Bills", f"{results['Bills']:,}")

except Error as error:
    st.error(f"Database connection failed: {error}")

finally:
    if connection is not None and connection.is_connected():
        connection.close()