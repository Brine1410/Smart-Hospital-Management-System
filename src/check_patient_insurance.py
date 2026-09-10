from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
FILE = PROJECT_DIR / "cleaned_data" / "patient_insurance.csv"


df = pd.read_csv(FILE)

duplicates = df[
    df["policy_number"].duplicated(keep=False)
].sort_values("policy_number")


print("=" * 70)
print("DUPLICATE POLICY NUMBER CHECK")
print("=" * 70)

print(f"\nTotal rows: {len(df):,}")
print(f"Duplicate rows: {len(duplicates):,}")

print("\nDuplicate policy numbers:")

print(
    duplicates[
        [
            "patient_insurance_id",
            "policy_number",
            "coverage_percentage",
            "policy_start_date",
            "policy_end_date",
            "patient_id",
            "insurance_provider_id"
        ]
    ].to_string(index=False)
)