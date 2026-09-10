from pathlib import Path

import mysql.connector
import pandas as pd


# ============================================================
# SMART HOSPITAL MANAGEMENT SYSTEM
# CLEANED CSV -> MYSQL DATA IMPORTER
# ============================================================

# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = PROJECT_DIR / "cleaned_data"


# ------------------------------------------------------------
# MYSQL CONNECTION SETTINGS
# ------------------------------------------------------------

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_NAME = "smart_hospital"

# MySQL password is entered when the script runs.
DB_PASSWORD = input("Enter MySQL password: ")


# ------------------------------------------------------------
# TABLE IMPORT ORDER
# Parent tables are imported before child tables
# to satisfy foreign-key constraints.
# ------------------------------------------------------------

TABLES = [
    ("department.csv", "department"),
    ("disease.csv", "disease"),
    ("drug_manufacturer.csv", "drug_manufacturer"),
    ("insurance_provider.csv", "insurance_provider"),
    ("patient.csv", "patient"),

    ("employee.csv", "employee"),
    ("ward.csv", "ward"),
    ("drug.csv", "drug"),
    ("diagnostic_test.csv", "diagnostic_test"),

    ("doctor.csv", "doctor"),
    ("bed.csv", "bed"),

    ("admission.csv", "admission"),
    ("drug_inventory.csv", "drug_inventory"),
    ("patient_insurance.csv", "patient_insurance"),
    ("prescription.csv", "prescription"),
    ("patient_diagnostic.csv", "patient_diagnostic"),

    ("billing.csv", "billing"),
    ("billing_detail.csv", "billing_detail"),

    ("staff_assignment.csv", "staff_assignment"),
]


# ------------------------------------------------------------
# CONVERT PANDAS VALUES TO MYSQL-SAFE VALUES
# ------------------------------------------------------------

def convert_value(value):
    """
    Convert Pandas/NumPy missing values and scalar values
    into normal Python values that MySQL Connector can use.
    """

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass

    return value


# ------------------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------------------

def main():

    print("=" * 70)
    print("SMART HOSPITAL MANAGEMENT SYSTEM")
    print("CLEANED CSV -> MYSQL DATA IMPORT")
    print("=" * 70)

    # --------------------------------------------------------
    # CHECK CLEANED DATA FOLDER
    # --------------------------------------------------------

    if not CLEANED_DIR.exists():

        print("\nERROR: cleaned_data folder was not found.")

        print(f"Expected location:")
        print(CLEANED_DIR)

        return

    print("\nCleaned data folder:")
    print(CLEANED_DIR)

    # --------------------------------------------------------
    # CONNECT TO MYSQL
    # --------------------------------------------------------

    print("\nConnecting to MySQL...")

    try:

        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()

        print("SUCCESS!")
        print("Python is connected to MySQL.")
        print(f"Database: {DB_NAME}")

    except mysql.connector.Error as error:

        print("\nERROR: Could not connect to MySQL.")
        print(error)

        return

    # --------------------------------------------------------
    # SAFETY CHECK
    # Make sure tables are empty before importing.
    # --------------------------------------------------------

    print("\nChecking existing table data...")

    existing_data = []

    for _, table_name in TABLES:

        cursor.execute(
            f"SELECT COUNT(*) FROM `{table_name}`"
        )

        count = cursor.fetchone()[0]

        if count > 0:

            existing_data.append(
                (table_name, count)
            )

    if existing_data:

        print("\nIMPORT STOPPED FOR SAFETY.")

        print("The following tables already contain data:")

        for table_name, count in existing_data:

            print(
                f"  {table_name:<22} {count:>10,} rows"
            )

        print("\nNo data was inserted.")

        cursor.close()
        connection.close()

        return

    # --------------------------------------------------------
    # IMPORT TABLES
    # --------------------------------------------------------

    total_rows = 0

    try:

        for csv_file, table_name in TABLES:

            print("\n" + "-" * 70)

            print(f"CSV file : {csv_file}")
            print(f"Table    : {table_name}")

            csv_path = CLEANED_DIR / csv_file

            # Check file exists
            if not csv_path.exists():

                raise FileNotFoundError(
                    f"Missing cleaned file:\n{csv_path}"
                )

            # Read cleaned CSV
            df = pd.read_csv(csv_path)

            print(f"Rows found: {len(df):,}")

            # Empty table
            if len(df) == 0:

                print("Table is empty. Skipping.")

                continue

            # ------------------------------------------------
            # BUILD INSERT QUERY
            # ------------------------------------------------

            columns = list(df.columns)

            column_sql = ", ".join(
                f"`{column}`"
                for column in columns
            )

            placeholders = ", ".join(
                ["%s"] * len(columns)
            )

            insert_sql = f"""
                INSERT INTO `{table_name}`
                ({column_sql})
                VALUES ({placeholders})
            """

            # ------------------------------------------------
            # CONVERT DATAFRAME ROWS
            # ------------------------------------------------

            rows = []

            for row in df.itertuples(
                index=False,
                name=None
            ):

                cleaned_row = tuple(
                    convert_value(value)
                    for value in row
                )

                rows.append(cleaned_row)

            # ------------------------------------------------
            # INSERT IN BATCHES
            # ------------------------------------------------

            batch_size = 1000

            for start in range(
                0,
                len(rows),
                batch_size
            ):

                batch = rows[
                    start:start + batch_size
                ]

                cursor.executemany(
                    insert_sql,
                    batch
                )

                inserted_so_far = min(
                    start + batch_size,
                    len(rows)
                )

                print(
                    f"  Inserted "
                    f"{inserted_so_far:,}/"
                    f"{len(rows):,}"
                )

            # Commit this table
            connection.commit()

            total_rows += len(rows)

            print(
                f"SUCCESS: {table_name} imported."
            )

    except Exception as error:

        print("\n" + "=" * 70)
        print("IMPORT FAILED")
        print("=" * 70)

        print(f"\nError:")
        print(error)

        print("\nRolling back the current transaction...")

        connection.rollback()

    else:

        # ----------------------------------------------------
        # IMPORT SUCCESS
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("IMPORT COMPLETED SUCCESSFULLY")
        print("=" * 70)

        print(
            f"\nTotal rows imported: "
            f"{total_rows:,}"
        )

        # ----------------------------------------------------
        # FINAL VERIFICATION
        # ----------------------------------------------------

        print("\nFinal MySQL table counts:")

        print("-" * 45)

        for _, table_name in TABLES:

            cursor.execute(
                f"SELECT COUNT(*) FROM `{table_name}`"
            )

            count = cursor.fetchone()[0]

            print(
                f"{table_name:<25} {count:>10,}"
            )

        print("-" * 45)

    finally:

        cursor.close()
        connection.close()

        print("\nMySQL connection closed.")


# ------------------------------------------------------------
# PROGRAM START
# ------------------------------------------------------------

if __name__ == "__main__":
    main()