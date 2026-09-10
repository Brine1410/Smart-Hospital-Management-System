import pandas as pd
import streamlit as st
from db import run_query

st.set_page_config(page_title="SQL Queries", page_icon="⚡", layout="wide")

st.title("⚡ SQL Queries & DBMS Demonstrations")

# Password check
if not st.session_state.get("db_password"):
    st.warning("Please enter your MySQL root password on the Home page sidebar first.")
    st.stop()

st.write(
    "Explore prebuilt complex SQL queries demonstrating relational concepts (Multi-table JOINs, Aggregates, Subqueries, Window Functions, and Date Analysis)."
)

# Define Prebuilt Queries
PREBUILT_QUERIES = [
    {
        "id": 1,
        "title": "1. Multi-Table JOIN (5 Tables): Patient Admission Details",
        "description": "Joins patient, admission, disease, ward, and department tables to provide comprehensive patient admission records.",
        "sql": """SELECT 
    p.patient_id,
    p.gender,
    p.city,
    a.admission_id,
    a.admission_date,
    a.discharge_date,
    a.admission_type,
    d.disease_name,
    d.disease_category,
    w.ward_name,
    dept.department_name
FROM patient p
JOIN admission a ON p.patient_id = a.patient_id
JOIN disease d ON a.disease_id = d.disease_id
JOIN ward w ON a.ward_id = w.ward_id
JOIN department dept ON a.department_id = dept.department_id
ORDER BY a.admission_date DESC
LIMIT 50;""",
        "chart": False,
    },
    {
        "id": 2,
        "title": "2. GROUP BY, Aggregates & HAVING: Department Admission Metrics",
        "description": "Aggregates total admissions and average length of stay per department, filtered using HAVING for departments with at least 50 admissions.",
        "sql": """SELECT 
    dept.department_name,
    dept.department_type,
    COUNT(a.admission_id) AS total_admissions,
    ROUND(AVG(DATEDIFF(IFNULL(a.discharge_date, CURRENT_DATE), a.admission_date)), 1) AS avg_stay_days
FROM department dept
JOIN admission a ON dept.department_id = a.department_id
GROUP BY dept.department_id, dept.department_name, dept.department_type
HAVING COUNT(a.admission_id) >= 50
ORDER BY total_admissions DESC;""",
        "chart": True,
        "chart_x": "department_name",
        "chart_y": "total_admissions",
    },
    {
        "id": 3,
        "title": "3. Subquery: Admissions Exceeding Average Hospital Billing",
        "description": "Uses a scalar subquery to find billing records where total amount exceeds the overall average bill across all patients.",
        "sql": """SELECT 
    b.bill_id,
    b.admission_id,
    p.patient_id,
    p.city,
    b.total_amount,
    b.payment_status
FROM billing b
JOIN admission a ON b.admission_id = a.admission_id
JOIN patient p ON a.patient_id = p.patient_id
WHERE b.total_amount > (
    SELECT AVG(total_amount) FROM billing
)
ORDER BY b.total_amount DESC
LIMIT 50;""",
        "chart": False,
    },
    {
        "id": 4,
        "title": "4. Window Functions: Doctor Diagnostics Ranking per Department",
        "description": "Uses RANK() window function partitioned by department to rank doctors based on total diagnostic tests conducted.",
        "sql": """SELECT 
    dept.department_name,
    emp.employee_name AS doctor_name,
    doc.specialization,
    COUNT(pd.patient_diagnostic_id) AS total_tests_conducted,
    RANK() OVER (
        PARTITION BY dept.department_id 
        ORDER BY COUNT(pd.patient_diagnostic_id) DESC
    ) AS dept_doctor_rank
FROM doctor doc
JOIN employee emp ON doc.employee_id = emp.employee_id
JOIN department dept ON emp.department_id = dept.department_id
LEFT JOIN patient_diagnostic pd ON doc.doctor_id = pd.doctor_id
GROUP BY dept.department_id, dept.department_name, doc.doctor_id, emp.employee_name, doc.specialization
ORDER BY dept.department_name, dept_doctor_rank
LIMIT 50;""",
        "chart": False,
    },
    {
        "id": 5,
        "title": "5. LEFT JOIN: Unmatched Patients Without Insurance Coverage",
        "description": "Identifies registered patients who have no insurance policies linked in the patient_insurance table.",
        "sql": """SELECT 
    p.patient_id,
    p.gender,
    p.blood_group,
    p.city,
    p.contact_number
FROM patient p
LEFT JOIN patient_insurance pi ON p.patient_id = pi.patient_id
WHERE pi.patient_insurance_id IS NULL
LIMIT 50;""",
        "chart": False,
    },
    {
        "id": 6,
        "title": "6. Date-Based Analysis: Monthly Admissions Breakdown",
        "description": "Groups admissions by month to track emergency vs elective admissions and average stay duration over time.",
        "sql": """SELECT 
    DATE_FORMAT(admission_date, '%Y-%m') AS admission_month,
    COUNT(admission_id) AS total_admissions,
    COUNT(CASE WHEN admission_type = 'Emergency' THEN 1 END) AS emergency_count,
    COUNT(CASE WHEN admission_type = 'Elective' THEN 1 END) AS elective_count,
    ROUND(AVG(DATEDIFF(IFNULL(discharge_date, CURRENT_DATE), admission_date)), 1) AS avg_stay_days
FROM admission
GROUP BY DATE_FORMAT(admission_date, '%Y-%m')
ORDER BY admission_month DESC;""",
        "chart": True,
        "chart_x": "admission_month",
        "chart_y": "total_admissions",
    },
    {
        "id": 7,
        "title": "7. Revenue Analysis: Billing Breakdown by Charge Type",
        "description": "Combines billing and billing_detail to calculate total revenue generated across room, drug, test, and procedure charges.",
        "sql": """SELECT 
    bd.charge_type,
    b.payment_status,
    COUNT(DISTINCT b.bill_id) AS total_bills,
    SUM(bd.amount) AS total_revenue,
    ROUND(AVG(bd.amount), 2) AS avg_charge_amount
FROM billing_detail bd
JOIN billing b ON bd.bill_id = b.bill_id
GROUP BY bd.charge_type, b.payment_status
ORDER BY total_revenue DESC;""",
        "chart": False,
    },
    {
        "id": 8,
        "title": "8. Inventory Analysis: Low Stock & Reorder Alert Report",
        "description": "Filters drug inventory records where current stock is at or below the designated reorder threshold level.",
        "sql": """SELECT 
    d.drug_id,
    d.drug_name,
    d.brand_name,
    d.drug_category,
    di.current_stock,
    di.reorder_level,
    (di.reorder_level - di.current_stock) AS deficit_amount,
    dm.manufacturer_name,
    dm.reliability_rating
FROM drug_inventory di
JOIN drug d ON di.drug_id = d.drug_id
JOIN drug_manufacturer dm ON d.manufacturer_id = dm.manufacturer_id
WHERE di.current_stock <= di.reorder_level
ORDER BY deficit_amount DESC;""",
        "chart": False,
    },
    {
        "id": 9,
        "title": "9. Facility Management: Ward Bed Occupancy Breakdown",
        "description": "Calculates available vs occupied bed counts and overall bed occupancy percentages across all hospital wards.",
        "sql": """SELECT 
    w.ward_id,
    w.ward_name,
    w.ward_type,
    dept.department_name,
    w.total_beds,
    COUNT(CASE WHEN b.bed_status = 'Occupied' THEN 1 END) AS occupied_beds,
    COUNT(CASE WHEN b.bed_status = 'Available' THEN 1 END) AS available_beds,
    ROUND((COUNT(CASE WHEN b.bed_status = 'Occupied' THEN 1 END) * 100.0 / w.total_beds), 1) AS occupancy_percentage
FROM ward w
JOIN department dept ON w.department_id = dept.department_id
LEFT JOIN bed b ON w.ward_id = b.ward_id
GROUP BY w.ward_id, w.ward_name, w.ward_type, dept.department_name, w.total_beds
ORDER BY occupancy_percentage DESC;""",
        "chart": False,
    },
    {
        "id": 10,
        "title": "10. Clinical Trends: Top 10 Most Frequent Diseases",
        "description": "Identifies the top 10 diseases diagnosed across admissions along with total billing revenue generated.",
        "sql": """SELECT 
    d.disease_id,
    d.disease_name,
    d.disease_category,
    COUNT(a.admission_id) AS total_admissions,
    SUM(b.total_amount) AS total_billing_generated,
    ROUND(AVG(b.total_amount), 2) AS avg_cost_per_case
FROM disease d
JOIN admission a ON d.disease_id = a.disease_id
LEFT JOIN billing b ON a.admission_id = b.admission_id
GROUP BY d.disease_id, d.disease_name, d.disease_category
ORDER BY total_admissions DESC
LIMIT 10;""",
        "chart": True,
        "chart_x": "disease_name",
        "chart_y": "total_admissions",
    },
]

st.header("Prebuilt SQL Query Library")

for q in PREBUILT_QUERIES:
    with st.expander(q["title"], expanded=(q["id"] == 1)):
        st.write(f"**Description:** {q['description']}")
        st.code(q["sql"], language="sql")
        button_key = f"run_btn_{q['id']}"
        if st.button(f"Run Query #{q['id']}", key=button_key):
            df_result = run_query(q["sql"])
            st.subheader(f"Results ({len(df_result)} rows)")
            st.dataframe(df_result, use_container_width=True, hide_index=True)

            if q.get("chart") and not df_result.empty:
                chart_df = df_result.set_index(q["chart_x"])[q["chart_y"]]
                st.subheader("Visual Analysis")
                st.bar_chart(chart_df)

st.write("---")

# Free-Text Custom SQL Query Runner
st.header("Custom SQL Query Sandbox")
st.write(
    "Write and execute your own custom `SELECT` or `WITH` queries against the database."
)

default_custom_sql = (
    "SELECT department_name, department_type, floor_number FROM department;"
)
user_sql = st.text_area(
    "Enter SQL SELECT Statement:",
    value=default_custom_sql,
    height=120,
)

if st.button("Execute Custom Query"):
    cleaned_sql = user_sql.strip()
    upper_sql = cleaned_sql.upper()

    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        st.error(
            "Security Policy Restriction: Only SELECT or WITH queries are permitted in the custom query sandbox."
        )
    elif ";" in cleaned_sql.rstrip(";"):
        st.error(
            "Multiple SQL statements (containing semicolons) are not permitted."
        )
    else:
        df_custom = run_query(cleaned_sql)
        st.subheader(f"Query Results ({len(df_custom)} rows)")
        st.dataframe(df_custom, use_container_width=True, hide_index=True)
