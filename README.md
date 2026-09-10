# Smart Hospital Management System

A relational database project built for a DBMS course. It models the core operations of a hospital — patients, admissions, doctors, wards, beds, prescriptions, diagnostics, drug inventory, insurance, and billing — in **MySQL 8**, with a Python ETL pipeline to load data and a lightweight **Streamlit** interface to explore and query it.

The focus of the project is the database design and SQL. The frontend exists to demonstrate the schema, constraints, and queries — not to be a polished application.

## Tech Stack

| Layer | Technology |
|---|---|
| Database | MySQL 8.0 (InnoDB, utf8mb4) |
| ETL / data loading | Python 3, pandas, mysql-connector-python |
| Frontend | Streamlit |

## Repository Structure

```
.
├── database/
│   └── smart_hospital_database.sql   # Full DDL: 19 tables, PKs, FKs, CHECK constraints
├── data/                             # Original raw CSV dataset (19 files)
├── cleaned_data/                     # Cleaned CSVs used by the importer
│   └── data_cleaning_report.csv      # Summary of cleaning steps applied
├── src/
│   ├── import_data.py                # ETL: loads cleaned CSVs into MySQL in FK-safe order
│   ├── test_connection.py            # Quick MySQL connectivity check
│   ├── check_patient_insurance.py    # Data-quality check for duplicate policy numbers
│   ├── db.py                         # Shared DB helper used by the Streamlit app
│   ├── app.py                        # Streamlit home page
│   └── pages/
│       ├── 1_Browse_Tables.py        # Inspect any table's columns, types, and rows
│       ├── 2_SQL_Queries.py          # Prebuilt analytical queries + free SQL sandbox
│       ├── 3_Search.py               # Patient lookup with linked records across tables
│       ├── 4_Manage_Records.py       # Minimal CRUD to demonstrate constraint enforcement
│       └── 5_Schema.py               # FK / CHECK constraint metadata from INFORMATION_SCHEMA
├── requirements.txt
└── .gitignore
```

## Database Schema

19 tables, organised as:

**Master tables** — `department`, `disease`, `drug_manufacturer`, `insurance_provider`, `patient`

**Dependent tables** — `employee`, `ward`, `drug`, `diagnostic_test`, `doctor`, `bed`

**Transactional tables** — `admission`, `drug_inventory`, `patient_insurance`, `prescription`, `patient_diagnostic`, `billing`, `billing_detail`, `staff_assignment`

Key design points:
- Every table has an explicit primary key.
- Foreign keys use `ON UPDATE CASCADE` and `ON DELETE RESTRICT` to prevent orphaned records.
- `CHECK` constraints enforce domain rules (e.g. coverage percentage 0–100, policy end date ≥ start date, non-negative floor numbers, manufacturer rating 0–5).
- Tables are created and populated in parent → child order to satisfy referential integrity.

The full DDL is in `database/smart_hospital_database.sql` and is also viewable inside the app on the **Schema** page.

## Dataset

Synthetic hospital HMIS dataset, 19 CSV files. After cleaning and import, the database contains approximately **392,000 rows**, including:

| Table | Rows |
|---|---|
| patient | 30,000 |
| admission | 45,000 |
| billing | 45,000 |
| billing_detail | 112,402 |
| prescription | 73,109 |
| patient_diagnostic | 63,269 |
| patient_insurance | 21,617 |

> **Note on `patient_insurance`:** the dataset contains four policy numbers that are shared by different patients. The original schema had a `UNIQUE` constraint on `policy_number`, which caused the import to fail. That constraint was removed so the data loads as-is. `src/check_patient_insurance.py` lists the affected rows.

## Setup

### Prerequisites
- Python 3.10+
- MySQL Server 8.0 running locally on port 3306
- A MySQL user with permission to create databases (the scripts assume `root`)

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/Brine1410/Smart-Hospital-Management-System.git
cd Smart-Hospital-Management-System

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Create the database schema

> ⚠️ The script starts with `DROP DATABASE IF EXISTS smart_hospital;` — it will wipe any existing database of that name.

```bash
mysql -u root -p < database/smart_hospital_database.sql
```

On Windows, if `mysql` is not on your PATH:

```powershell
cmd /c '"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < ".\database\smart_hospital_database.sql"'
```

You should see a table listing all 19 tables with `0` rows.

### 3. Load the data

```bash
python src/import_data.py
```

Enter your MySQL password when prompted. The script refuses to run if any table already contains data, so it is safe to re-run after a fresh schema creation. On success it prints final row counts for every table.

### 4. Run the Streamlit app

```bash
python -m streamlit run src/app.py
```

Open `http://localhost:8501`, enter your MySQL password in the sidebar, and browse the pages.

## App Pages

| Page | What it demonstrates |
|---|---|
| **Home** | Live row counts for all 19 tables |
| **Browse Tables** | Column names and data types from `INFORMATION_SCHEMA`, row previews |
| **SQL Queries** | 10 prebuilt queries: multi-table JOINs, GROUP BY / HAVING, subqueries, window functions (`RANK`, `ROW_NUMBER`), LEFT JOIN anti-patterns, date trends, revenue analysis, low-stock reports, bed occupancy. Also a free-text sandbox restricted to `SELECT` / `WITH` |
| **Search** | Parameterized patient lookup; shows linked admissions, prescriptions, diagnostics, insurance, and billing via JOINs |
| **Manage Records** | INSERT / UPDATE / DELETE on `department` and `insurance_provider`. Intentionally lets you trigger FK, CHECK, and duplicate-key errors so constraint enforcement is visible |
| **Schema** | Foreign key and CHECK constraint metadata from `INFORMATION_SCHEMA`, plus the full DDL |

## Security Notes

- No credentials are stored in the repository. The MySQL password is entered at runtime (terminal prompt for scripts, sidebar for the app) and kept only in memory.
- All queries that take user input use parameterized placeholders (`%s`); no SQL is built with string formatting.
- `.env`, `.venv/`, and anything matching `*password*` or `*credentials*` are excluded via `.gitignore`.

## Contributors

- **Brine1410** — database design, schema, data cleaning, ETL pipeline
- **Raed-Tanwar** — Streamlit frontend, schema fix for `patient_insurance`

## License

Academic project. Not intended for production or real patient data.
