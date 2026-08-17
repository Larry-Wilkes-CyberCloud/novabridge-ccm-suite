import pandas as pd

employees = pd.read_csv("data/employees.csv")
print(employees.head())
print(employees.shape)
print(employees["status"].value_counts())