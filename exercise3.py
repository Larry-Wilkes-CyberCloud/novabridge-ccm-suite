import pandas as pd

invoices = pd.read_csv("data/invoices.csv")
invoices["invoice_date"] = pd.to_datetime(invoices["invoice_date"])

# Group by vendor + amount, look for multiple invoices within a few days of each other
invoices_sorted = invoices.sort_values(["vendor_id", "amount", "invoice_date"])

duplicates = []
for (vendor, amount), group in invoices_sorted.groupby(["vendor_id", "amount"]):
    if len(group) > 1:
        dates = group["invoice_date"].tolist()
        for i in range(len(dates) - 1):
            gap = (dates[i+1] - dates[i]).days
            if gap <= 7:  # same vendor, same amount, within a week
                duplicates.append(group.iloc[[i, i+1]])

if duplicates:
    dup_df = pd.concat(duplicates).drop_duplicates()
    print(f"Potential duplicate payments found: {len(dup_df)} invoice rows")
    print(dup_df[["invoice_id", "vendor_name", "amount", "invoice_date"]].sort_values(["vendor_name", "amount"]))
    print(f"\nTotal dollar exposure: ${dup_df['amount'].sum():,.2f}")
else:
    print("No potential duplicates found")
