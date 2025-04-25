import pandas as pd
import matplotlib.pyplot as plt

total_rows = 0
null_name_rows = 0
hire_pre_2015 = 0
exactly_two_names = 0
hire_pre_birth_date = 0
do_report_self = 0
manager_no_exist = 0
share_phone = 0
city_one_or_less = 0
age_less_18 = 0

df = pd.read_csv('employees.csv', parse_dates=['birth_date', 'hire_date'])
df.columns = df.columns.str.strip()
print(df.columns.tolist())
current_date = pd.to_datetime('2025-04-24')

cities_dict = {}
ages = {}

for index, row in df.iterrows():
    total_rows += 1

    # name = row['name']
    # address = row['address']
    # if pd.isna(name) or str(name).strip() == "" or pd.isna(address) or str(address).strip() == "":
    #     null_name_rows += 1

    # hire_date = row['hire_date']
    # if hire_date < pd.to_datetime('2015-01-01'):
    #     hire_pre_2015 += 1

    # if len(str(name).split(" ")) != 2:
    #     exactly_two_names += 1

    # birth_date = row['birth_date']
    # if hire_date < birth_date:
    #     hire_pre_birth_date += 1

    # if row['name'] == row['reports_to']:
    #     do_report_self += 1

    # report_to = row['reports_to']
    # if str(report_to) not in df['eid'].astype(str).values:
    #     manager_no_exist += 1

    # if total_rows % 10 == 0:
    #     print(f"Current Row: {total_rows}")
    # phone = row['phone']
    # for jndex, jow in df.iterrows():
    #     if jndex == index:
    #         continue
    #     if str(phone) == str(jow['phone']):
    #         share_phone += 1
    #         break

    # city = row['city']
    # if city in cities_dict:
    #     cities_dict[city] += 1
    # else:
    #     cities_dict[city] = 1

    # birth_date = row['birth_date']
    # age = current_date.year - birth_date.year
    # if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
    #     age -= 1
    # if age < 18:
    #     age_less_18 += 1

    birth_date = row['birth_date']
    age = current_date.year - birth_date.year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    if age in ages:
        ages[age] += 1
    else:
        ages[age] = 1

# ranges = [0, 30000, 60000, 90000, 120000, 150000]
# df['salary'].hist(bins=ranges, edgecolor='black', density=True)

# plt.title('Salary Distribution')
# plt.xlabel('Salary')
# plt.ylabel('Frequency')
# plt.show()

plt.xlim(0, 80)
plt.bar(ages.keys(), ages.values(), color='skyblue', edgecolor='black')
plt.title('Age Distribution')
plt.xlabel('Age')
plt.ylabel('Frequency')
plt.show()


for city, count in cities_dict.items():
    if count < 2:
        city_one_or_less += 1

print(f"Total rows: {total_rows}")
print(f"Null Names Rows: {null_name_rows}")
print(f"Hire Post 2015: {hire_pre_2015}")
print(f"Exactly two names: {exactly_two_names}")
print(f"Hire date before birth date: {hire_pre_birth_date}")
print(f"Employee reports to self: {do_report_self}")
print(f"Manager doesn't exist: {manager_no_exist}")
print(f"Share phone numbers: {share_phone}")
print(f"City has one or less people: {city_one_or_less}")
print(f"Employees under 18: {age_less_18}")