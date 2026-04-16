import pandas as pd

RAW_DATASET = "ML_Dataset_5000_FINAL_dirty(1).csv"
CLEAN_DATASET = "ML_Feature_Set_Cleaned.csv"

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(RAW_DATASET)

# =========================
# DATA CLEANING
# =========================

# Remove duplicates
df = df.drop_duplicates().reset_index(drop=True)

# Convert to numeric
numeric_cols = ["CGPA", "Internships", "Projects", "AptitudeTestScore", "Certificates"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Handle missing values
df = df.fillna(df.median(numeric_only=True))

# Valid ranges
df = df[(df["CGPA"] >= 0) & (df["CGPA"] <= 10)]
df = df[(df["AptitudeTestScore"] >= 0) & (df["AptitudeTestScore"] <= 100)]
df = df[(df["Internships"] >= 0)]
df = df[(df["Projects"] >= 0)]
df = df[(df["Certificates"] >= 0)]

# Light IQR outlier removal
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]

df = df.reset_index(drop=True)

# =========================
# SAVE CLEANED DATA
# =========================
df.to_csv(CLEAN_DATASET, index=False)

print("Cleaning complete!")
