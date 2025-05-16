import pandas as pd
import us_state_abbrev as st
import seaborn as sns
import matplotlib.pyplot as plt


census_df = pd.read_csv('acs2017_county_data.csv'
                        , usecols=lambda col: col.strip() in ['County', 'State', 'TotalPop'
                                                              , 'IncomePerCap', 'Poverty', 'Unemployment'])
cases_df = pd.read_csv('covid_confirmed_usafacts.csv'
                       , usecols=lambda col: col.strip() in ['County Name', 'State', '2023-07-23'])
deaths_df = pd.read_csv('covid_deaths_usafacts.csv'
                        , usecols=lambda col: col.strip() in ['County Name', 'State', '2023-07-23'])

census_df.columns = census_df.columns.str.strip()
cases_df.columns = cases_df.columns.str.strip()
deaths_df.columns = deaths_df.columns.str.strip()

print(census_df.columns)
print(cases_df.columns)
print(deaths_df.columns)

print("----Starting attributes----")
print()
print(f"Census df:")
print(f"no. Rows = {census_df.shape[0]}")
print()
print(f"Cases df:")
print(f"no. Rows = {cases_df.shape[0]}")
print()
print(f"Deaths df:")
print(f"no Rows = {deaths_df.shape[0]}")

#challenge 1
cases_df['County Name'] = cases_df['County Name'].str.strip()
deaths_df['County Name'] = deaths_df['County Name'].str.strip()
print()
print("###Challenge 1###")
print(f"Counties named Washington: {(cases_df['County Name'] == 'Washington County').sum() \
                                   + (deaths_df['County Name'] == 'Washington County').sum()}")

#challenge 2
cases_df = cases_df[cases_df['County Name'] != 'Statewide Unallocated']
deaths_df = deaths_df[deaths_df['County Name'] != 'Statewide Unallocated']
print()
print("###Challenge 2###")
print()
print(f"Cases df:")
print(f"no. Rows = {cases_df.shape[0]}")
print()
print(f"Deaths df:")
print(f"no Rows = {deaths_df.shape[0]}")

#Challenge 3
cases_df['State'] = cases_df['State'].map(st.abbrev_to_us_state)
deaths_df['State'] = deaths_df['State'].map(st.abbrev_to_us_state)

print()
print("###Challenge 3###")
print()
print(f"Cases rows:")
print(cases_df.head(3))
print()
print(f"Deaths rows:")
print(deaths_df.head(3))

#Challenge 4
census_df['key'] = census_df['County'] + census_df['State']
cases_df['key'] = cases_df['County Name'] + cases_df['State']
deaths_df['key'] = deaths_df['County Name'] + deaths_df['State']
census_df.set_index('key', inplace=True)
cases_df.set_index('key', inplace=True)
deaths_df.set_index('key', inplace=True)

print()
print("###Challenge 4###")
print()
print(f"Census rows:")
print(census_df.head(3))
print()
print(f"Cases rows:")
print(cases_df.head(3))
print()
print(f"Deaths rows:")
print(deaths_df.head(3))

#Challenge 5
cases_df.rename(columns={'2023-07-23' : 'Cases'}, inplace=True)
deaths_df.rename(columns={'2023-07-23' : 'Deaths'}, inplace=True)

print()
print("###Challenge 5###")
print()
print("Cases columns:")
print(cases_df.columns.values.tolist())
print()
print("Deaths columns:")
print(deaths_df.columns.values.tolist())

#integration
join_df = census_df.merge(cases_df.drop(columns=['State', 'County Name']), on='key', how='left') \
                    .merge(deaths_df.drop(columns=['State', 'County Name']), on='key', how='left')
join_df['CasesPerCap'] = join_df['Cases'] / join_df['TotalPop']
join_df['DeathsPerCap'] = join_df['Deaths'] / join_df['TotalPop']

print()
print("###Challenge 5###")
print()
print(f"Join df rows: {join_df.shape[0]}")

#Analyze
corr_matrix = join_df.select_dtypes(include='number').corr()
print()
print(corr_matrix)

#Heatmap
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)

print()
plt.title('Correlation Matrix Heatmap')
plt.show()
