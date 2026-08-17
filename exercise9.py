import pandas as pd
import numpy as np

np.random.seed(1)
invoices = pd.read_csv("data/invoices.csv")

# --- Stratified sampling: sample proportionally by vendor ---
sample_frac = 0.10  # test 10% of the population
stratified_sample = invoices.groupby("vendor_id", group_keys=False).sample(frac=sample_frac, random_state=1)
print(f"Stratified sample size: {len(stratified_sample)} of {len(invoices)}")
print(stratified_sample["vendor_id"].value_counts().sort_index())

print()

# --- Monetary-unit sampling: probability of selection weighted by dollar amount ---
n_mus_samples = 30
weights = invoices["amount"] / invoices["amount"].sum()
mus_sample = invoices.sample(n=n_mus_samples, weights=weights, random_state=1, replace=False)
print(f"MUS sample size: {len(mus_sample)}")
print(f"MUS sample covers ${mus_sample['amount'].sum():,.2f} of ${invoices['amount'].sum():,.2f} total population value "
      f"({mus_sample['amount'].sum()/invoices['amount'].sum()*100:.1f}%)")
print(f"Average dollar amount in MUS sample: ${mus_sample['amount'].mean():,.2f} vs. population average: ${invoices['amount'].mean():,.2f}")
