import pandas as pd

access = pd.read_csv("data/access_rights.csv")
employees = pd.read_csv("data/employees.csv")

conflicts = access[(access["can_approve_po"] == True) & (access["can_create_vendor"] == True)]
conflicts = conflicts.merge(employees[["employee_id", "name", "department"]], on="employee_id")

print(f"Employees with SoD conflicts (can approve POs AND create vendors): {len(conflicts)}")
print(conflicts[["employee_id", "name", "department"]])
