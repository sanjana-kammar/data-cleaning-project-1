"""
DecodeLabs - Data Analytics - Project 1: Data Cleaning & Preparation
Usage:  python clean_data.py
Input : Dataset_for_Data_Analytics.xlsx
Output: cleaned_dataset.csv  (+ verification printout)
"""
import re
import pandas as pd

INPUT = "Dataset_for_Data_Analytics.xlsx"
OUTPUT = "cleaned_dataset.csv"

df = pd.read_excel(INPUT)
rows_before = len(df)

# ---------- PHASE 0: AUDIT (before) ----------
print("=== AUDIT (BEFORE) ===")
print("Rows:", rows_before)
print("Missing values per column:\n", df.isnull().sum()[df.isnull().sum() > 0])
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate OrderIDs:", df["OrderID"].duplicated().sum())

# ---------- PHASE 1: MISSING VALUES ----------
# CouponCode is blank when the customer used no coupon, so imputing the
# mode (e.g. 'FREESHIP') would invent discounts. Use an explicit label instead.
df["CouponCode"] = df["CouponCode"].fillna("NO_COUPON")

# ---------- PHASE 2: DUPLICATES ----------
df = df.drop_duplicates()
df = df.drop_duplicates(subset="OrderID", keep="first")

# ---------- PHASE 3: FORMATS ----------
text_cols = ["OrderID", "CustomerID", "Product", "ShippingAddress", "PaymentMethod",
             "OrderStatus", "TrackingNumber", "CouponCode", "ReferralSource"]
for c in text_cols:
    df[c] = df[c].astype(str).str.strip()

for c in ["Product", "PaymentMethod", "OrderStatus", "ReferralSource"]:
    df[c] = df[c].str.title()                      # Proper Case

df["OrderID"] = df["OrderID"].str.upper()
df["CustomerID"] = df["CustomerID"].str.upper()
df["TrackingNumber"] = df["TrackingNumber"].str.upper()
df["CouponCode"] = df["CouponCode"].str.upper()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")  # ISO 8601

df["Quantity"] = df["Quantity"].astype(int)
df["ItemsInCart"] = df["ItemsInCart"].astype(int)
df["UnitPrice"] = df["UnitPrice"].astype(float).round(2)
df["TotalPrice"] = df["TotalPrice"].astype(float).round(2)

df.to_csv(OUTPUT, index=False, float_format="%.2f")  # keeps 2 decimals (e.g. 2853.10)

# ---------- VERIFICATION GATE (Project 2 threshold) ----------
print("\n=== VERIFICATION (AFTER) ===")
dup_ids = int(df["OrderID"].duplicated().sum())
bad_dates = int((~df["Date"].astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}")).sum()
                + df["Date"].isnull().sum())
nulls = int(df.isnull().sum().sum())
total_mismatch = int(((df["Quantity"] * df["UnitPrice"]).round(2) - df["TotalPrice"]).abs().gt(0.01).sum())

print("Rows:", len(df), "(removed:", rows_before - len(df), ")")
print("Duplicate OrderIDs      :", dup_ids)
print("Incorrectly formatted dates:", bad_dates)
print("Remaining null values   :", nulls)
print("TotalPrice != Qty x UnitPrice:", total_mismatch)

assert dup_ids == 0 and bad_dates == 0 and nulls == 0, "Verification gate FAILED"
print("\nPASS: 0 duplicate IDs, 0 bad dates, 0 nulls")
