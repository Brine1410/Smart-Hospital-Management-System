-- Smart Hospital Management System
-- MySQL 8.0+
-- Phase 1: Database + relational schema
-- Source: Hospital HMIS synthetic dataset (19 CSV tables)

DROP DATABASE IF EXISTS smart_hospital;
CREATE DATABASE smart_hospital
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE smart_hospital;

-- =========================================================
-- 1. MASTER / PARENT TABLES
-- =========================================================

CREATE TABLE department (
    department_id INT UNSIGNED PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    department_type VARCHAR(30) NOT NULL,
    floor_number TINYINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    CONSTRAINT chk_department_floor CHECK (floor_number >= 0)
) ENGINE=InnoDB;

CREATE TABLE disease (
    disease_id INT UNSIGNED PRIMARY KEY,
    disease_name VARCHAR(100) NOT NULL,
    disease_category VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE drug_manufacturer (
    manufacturer_id INT UNSIGNED PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    reliability_rating DECIMAL(3,1) NOT NULL,
    contract_status VARCHAR(20) NOT NULL,
    CONSTRAINT chk_manufacturer_rating
        CHECK (reliability_rating BETWEEN 0 AND 5)
) ENGINE=InnoDB;

CREATE TABLE insurance_provider (
    insurance_provider_id INT UNSIGNED PRIMARY KEY,
    provider_name VARCHAR(150) NOT NULL,
    provider_type VARCHAR(30) NOT NULL,
    contact_details VARCHAR(30) NOT NULL,
    coverage_limit DECIMAL(14,2) NOT NULL,
    CONSTRAINT chk_insurance_limit CHECK (coverage_limit >= 0)
) ENGINE=InnoDB;

-- =========================================================
-- 2. PATIENT / STAFF / FACILITY TABLES
-- =========================================================

CREATE TABLE patient (
    patient_id INT UNSIGNED PRIMARY KEY,
    gender VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    city VARCHAR(100) NOT NULL,
    contact_number VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE employee (
    employee_id INT UNSIGNED PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    role VARCHAR(30) NOT NULL,
    employment_type VARCHAR(30) NOT NULL,
    date_of_joining DATE NOT NULL,
    department_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id)
        REFERENCES department(department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE doctor (
    doctor_id INT UNSIGNED PRIMARY KEY,
    employee_id INT UNSIGNED NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(20) NOT NULL,
    experience_years TINYINT UNSIGNED NOT NULL,

    CONSTRAINT uq_doctor_employee UNIQUE (employee_id),

    CONSTRAINT fk_doctor_employee
        FOREIGN KEY (employee_id)
        REFERENCES employee(employee_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_doctor_experience CHECK (experience_years >= 0)
) ENGINE=InnoDB;

CREATE TABLE ward (
    ward_id INT UNSIGNED PRIMARY KEY,
    ward_name VARCHAR(100) NOT NULL,
    ward_type VARCHAR(30) NOT NULL,
    total_beds SMALLINT UNSIGNED NOT NULL,
    department_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_ward_department
        FOREIGN KEY (department_id)
        REFERENCES department(department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_ward_beds CHECK (total_beds > 0)
) ENGINE=InnoDB;

CREATE TABLE bed (
    bed_id INT UNSIGNED PRIMARY KEY,
    bed_number VARCHAR(20) NOT NULL,
    bed_status VARCHAR(20) NOT NULL DEFAULT 'Available',
    ward_id INT UNSIGNED NOT NULL,

    CONSTRAINT uq_bed_ward_number UNIQUE (ward_id, bed_number),

    CONSTRAINT fk_bed_ward
        FOREIGN KEY (ward_id)
        REFERENCES ward(ward_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =========================================================
-- 3. PHARMACY
-- =========================================================

CREATE TABLE drug (
    drug_id INT UNSIGNED PRIMARY KEY,
    drug_name VARCHAR(100) NOT NULL,
    brand_name VARCHAR(150) NOT NULL,
    drug_category VARCHAR(50) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    manufacturer_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_drug_manufacturer
        FOREIGN KEY (manufacturer_id)
        REFERENCES drug_manufacturer(manufacturer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_drug_cost CHECK (unit_cost >= 0)
) ENGINE=InnoDB;

CREATE TABLE drug_inventory (
    inventory_id INT UNSIGNED PRIMARY KEY,
    current_stock INT UNSIGNED NOT NULL,
    reorder_level INT UNSIGNED NOT NULL,
    inventory_status VARCHAR(20) NOT NULL,
    last_restock_date DATE NOT NULL,
    drug_id INT UNSIGNED NOT NULL,

    CONSTRAINT uq_inventory_drug UNIQUE (drug_id),

    CONSTRAINT fk_inventory_drug
        FOREIGN KEY (drug_id)
        REFERENCES drug(drug_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =========================================================
-- 4. DIAGNOSTICS
-- =========================================================

CREATE TABLE diagnostic_test (
    test_id INT UNSIGNED PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    test_category VARCHAR(50) NOT NULL,
    standard_cost DECIMAL(10,2) NOT NULL,
    department_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_test_department
        FOREIGN KEY (department_id)
        REFERENCES department(department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_test_cost CHECK (standard_cost >= 0)
) ENGINE=InnoDB;

-- =========================================================
-- 5. CORE CLINICAL TRANSACTION
-- =========================================================

CREATE TABLE admission (
    admission_id INT UNSIGNED PRIMARY KEY,
    admission_date DATE NOT NULL,
    discharge_date DATE NULL,
    admission_type VARCHAR(30) NOT NULL,
    admission_status VARCHAR(30) NOT NULL,
    patient_id INT UNSIGNED NOT NULL,
    department_id INT UNSIGNED NOT NULL,
    ward_id INT UNSIGNED NOT NULL,
    bed_id INT UNSIGNED NOT NULL,
    disease_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_admission_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_admission_department
        FOREIGN KEY (department_id)
        REFERENCES department(department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_admission_ward
        FOREIGN KEY (ward_id)
        REFERENCES ward(ward_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_admission_bed
        FOREIGN KEY (bed_id)
        REFERENCES bed(bed_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_admission_disease
        FOREIGN KEY (disease_id)
        REFERENCES disease(disease_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_admission_dates
        CHECK (discharge_date IS NULL OR discharge_date >= admission_date)
) ENGINE=InnoDB;

CREATE TABLE prescription (
    prescription_id INT UNSIGNED PRIMARY KEY,
    dosage VARCHAR(50) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    duration_days SMALLINT UNSIGNED NOT NULL,
    admission_id INT UNSIGNED NOT NULL,
    drug_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_prescription_admission
        FOREIGN KEY (admission_id)
        REFERENCES admission(admission_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_prescription_drug
        FOREIGN KEY (drug_id)
        REFERENCES drug(drug_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_prescription_duration CHECK (duration_days > 0)
) ENGINE=InnoDB;

CREATE TABLE patient_diagnostic (
    patient_diagnostic_id INT UNSIGNED PRIMARY KEY,
    test_date DATE NOT NULL,
    result_status VARCHAR(30) NOT NULL,
    admission_id INT UNSIGNED NOT NULL,
    test_id INT UNSIGNED NOT NULL,
    doctor_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_patient_diagnostic_admission
        FOREIGN KEY (admission_id)
        REFERENCES admission(admission_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_patient_diagnostic_test
        FOREIGN KEY (test_id)
        REFERENCES diagnostic_test(test_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_patient_diagnostic_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =========================================================
-- 6. BILLING
-- =========================================================

CREATE TABLE billing (
    bill_id INT UNSIGNED PRIMARY KEY,
    bill_date DATE NOT NULL,
    total_amount DECIMAL(14,2) NOT NULL,
    insurance_covered_amount DECIMAL(14,2) NOT NULL DEFAULT 0,
    patient_payable_amount DECIMAL(14,2) NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    payment_mode VARCHAR(30) NOT NULL,
    admission_id INT UNSIGNED NOT NULL,

    CONSTRAINT uq_billing_admission UNIQUE (admission_id),

    CONSTRAINT fk_billing_admission
        FOREIGN KEY (admission_id)
        REFERENCES admission(admission_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_billing_total CHECK (total_amount >= 0),
    CONSTRAINT chk_billing_insurance CHECK (insurance_covered_amount >= 0),
    CONSTRAINT chk_billing_payable CHECK (patient_payable_amount >= 0),
    CONSTRAINT chk_billing_split
        CHECK (insurance_covered_amount + patient_payable_amount = total_amount)
) ENGINE=InnoDB;

CREATE TABLE billing_detail (
    billing_detail_id INT UNSIGNED PRIMARY KEY,
    charge_type VARCHAR(30) NOT NULL,
    reference_id INT UNSIGNED NULL,
    amount DECIMAL(14,2) NOT NULL,
    bill_id INT UNSIGNED NOT NULL,

    CONSTRAINT fk_billing_detail_bill
        FOREIGN KEY (bill_id)
        REFERENCES billing(bill_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_billing_detail_amount CHECK (amount >= 0)
) ENGINE=InnoDB;

-- NOTE:
-- reference_id is intentionally NOT declared as a foreign key.
-- Its meaning depends on charge_type (Room/Drug/Test/Procedure)
-- in the source dataset.

-- =========================================================
-- 7. INSURANCE
-- =========================================================

CREATE TABLE patient_insurance (
    patient_insurance_id INT UNSIGNED PRIMARY KEY,
    policy_number VARCHAR(30) NOT NULL,
    coverage_percentage DECIMAL(5,2) NOT NULL,
    policy_start_date DATE NOT NULL,
    policy_end_date DATE NOT NULL,
    patient_id INT UNSIGNED NOT NULL,
    insurance_provider_id INT UNSIGNED NOT NULL,

    CONSTRAINT uq_patient_insurance_policy UNIQUE (policy_number),

    CONSTRAINT fk_patient_insurance_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_patient_insurance_provider
        FOREIGN KEY (insurance_provider_id)
        REFERENCES insurance_provider(insurance_provider_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_insurance_coverage
        CHECK (coverage_percentage BETWEEN 0 AND 100),

    CONSTRAINT chk_policy_dates
        CHECK (policy_end_date >= policy_start_date)
) ENGINE=InnoDB;

-- =========================================================
-- 8. STAFF ↔ WARD ASSIGNMENT
-- =========================================================

CREATE TABLE staff_assignment (
    assignment_id INT UNSIGNED PRIMARY KEY,
    employee_id INT UNSIGNED NOT NULL,
    ward_id INT UNSIGNED NOT NULL,
    shift VARCHAR(20) NOT NULL,

    CONSTRAINT fk_staff_assignment_employee
        FOREIGN KEY (employee_id)
        REFERENCES employee(employee_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_staff_assignment_ward
        FOREIGN KEY (ward_id)
        REFERENCES ward(ward_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =========================================================
-- 9. INDEXES FOR COMMON COMMAND CENTER QUERIES
-- =========================================================

CREATE INDEX idx_patient_name
    ON patient(patient_id);

CREATE INDEX idx_employee_department
    ON employee(department_id);

CREATE INDEX idx_ward_department
    ON ward(department_id);

CREATE INDEX idx_bed_status
    ON bed(bed_status);

CREATE INDEX idx_admission_patient
    ON admission(patient_id);

CREATE INDEX idx_admission_status
    ON admission(admission_status);

CREATE INDEX idx_admission_dates
    ON admission(admission_date, discharge_date);

CREATE INDEX idx_admission_ward
    ON admission(ward_id);

CREATE INDEX idx_prescription_admission
    ON prescription(admission_id);

CREATE INDEX idx_prescription_drug
    ON prescription(drug_id);

CREATE INDEX idx_diagnostic_admission
    ON patient_diagnostic(admission_id);

CREATE INDEX idx_diagnostic_test
    ON patient_diagnostic(test_id);

CREATE INDEX idx_billing_payment_status
    ON billing(payment_status);

CREATE INDEX idx_billing_date
    ON billing(bill_date);

CREATE INDEX idx_billing_detail_charge_type
    ON billing_detail(charge_type);

CREATE INDEX idx_staff_assignment_ward
    ON staff_assignment(ward_id);

-- =========================================================
-- 10. QUICK VERIFICATION
-- =========================================================

SELECT
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.tables
WHERE table_schema = 'smart_hospital'
ORDER BY TABLE_NAME;
