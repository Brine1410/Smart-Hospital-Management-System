import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st


def get_connection(password=None):
    if password is None:
        password = st.session_state.get("db_password", "")
    if not password:
        raise ValueError("MySQL password is required. Please set it in the sidebar.")
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=password,
        database="smart_hospital",
    )


def run_query(sql, params=None, password=None):
    """Run a SELECT query and return results as a pandas DataFrame."""
    conn = None
    try:
        conn = get_connection(password)
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows, columns=columns)
    except Error as err:
        st.error(f"MySQL Error ({err.errno}): {err.msg}")
        return pd.DataFrame()
    except Exception as err:
        st.error(f"Error executing query: {err}")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()


def run_execute(sql, params=None, password=None):
    """Run INSERT/UPDATE/DELETE query with commit. Returns (success, result_message_or_rowcount)."""
    conn = None
    try:
        conn = get_connection(password)
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        return True, rowcount
    except Error as err:
        return False, f"MySQL Error [{err.errno}]: {err.msg}"
    except Exception as err:
        return False, f"Error: {err}"
    finally:
        if conn and conn.is_connected():
            conn.close()
