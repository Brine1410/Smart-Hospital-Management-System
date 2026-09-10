import streamlit as st

st.set_page_config(
    page_title="Smart Hospital Management System",
    page_icon="🏥",
    layout="wide",
)

# Password input in sidebar
st.sidebar.header("Database Connection")

default_password = st.session_state.get("db_password", "")
db_password = st.sidebar.text_input(
    "MySQL root password",
    value=default_password,
    type="password",
)

if db_password:
    st.session_state["db_password"] = db_password

# Streamlit Navigation setup using filled circle bullet points (●)
home_page = st.Page("home.py", title="Home", icon="●", default=True)
display_page = st.Page("pages/1_Display.py", title="Display", icon="●")
search_page = st.Page("pages/2_Search.py", title="Search", icon="●")
browse_page = st.Page("pages/3_Browse_Tables.py", title="Browse Tables", icon="●")
manage_page = st.Page("pages/4_Manage_Records.py", title="Manage Records", icon="●")
queries_page = st.Page("pages/5_SQL_Queries.py", title="SQL Queries", icon="●")
schema_page = st.Page("pages/6_Schema.py", title="Schema", icon="●")

pg = st.navigation(
    [
        home_page,
        display_page,
        search_page,
        browse_page,
        manage_page,
        queries_page,
        schema_page,
    ]
)

pg.run()