# this program loads Census ACS data using basic, slow INSERTs 
# run it with -h to see the command line options

import time
import psycopg2
import argparse
import re
import csv

DBname = "postgres"
DBuser = "postgres"
DBpwd = "Halo!331"   # insert your postgres db password here
TableName = 'CensusData'
Datafile = "filedoesnotexist"  # name of the data file to be loaded
CreateDB = False  # indicates whether the DB table should be (re)-created

def row2vals(row):
    for key in row:
        if not row[key]:
            row[key] = 0  # ENHANCE: handle the null vals
        row['County'] = row['County'].replace('\'','')  # TIDY: eliminate quotes within literals

    ret = f"""
       {row['TractId']},            -- TractId
       '{row['State']}',                -- State
       '{row['County']}',               -- County
       {row['TotalPop']},               -- TotalPop
       {row['Men']},                    -- Men
       {row['Women']},                  -- Women
       {row['Hispanic']},               -- Hispanic
       {row['White']},                  -- White
       {row['Black']},                  -- Black
       {row['Native']},                 -- Native
       {row['Asian']},                  -- Asian
       {row['Pacific']},                -- Pacific
       {row['VotingAgeCitizen']},       -- VotingAgeCitizen
       {row['Income']},                 -- Income
       {row['IncomeErr']},              -- IncomeErr
       {row['IncomePerCap']},           -- IncomePerCap
       {row['IncomePerCapErr']},        -- IncomePerCapErr
       {row['Poverty']},                -- Poverty
       {row['ChildPoverty']},           -- ChildPoverty
       {row['Professional']},           -- Professional
       {row['Service']},                -- Service
       {row['Office']},                 -- Office
       {row['Construction']},           -- Construction
       {row['Production']},             -- Production
       {row['Drive']},                  -- Drive
       {row['Carpool']},                -- Carpool
       {row['Transit']},                -- Transit
       {row['Walk']},                   -- Walk
       {row['OtherTransp']},            -- OtherTransp
       {row['WorkAtHome']},             -- WorkAtHome
       {row['MeanCommute']},            -- MeanCommute
       {row['Employed']},               -- Employed
       {row['PrivateWork']},            -- PrivateWork
       {row['PublicWork']},             -- PublicWork
       {row['SelfEmployed']},           -- SelfEmployed
       {row['FamilyWork']},             -- FamilyWork
       {row['Unemployment']}            -- Unemployment
    """

    return ret


def initialize():
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--datafile", required=True)
  parser.add_argument("-c", "--createtable", action="store_true")
  args = parser.parse_args()

  global Datafile
  Datafile = args.datafile
  global CreateDB
  CreateDB = args.createtable

# read the input data file into a list of row strings
def readdata(fname):
    print(f"readdata: reading from File: {fname}")
    with open(fname, mode="r") as fil:
        dr = csv.DictReader(fil)
        
        rowlist = []
        for row in dr:
            rowlist.append(row)

    return rowlist

# convert list of data rows into list of SQL 'INSERT INTO ...' commands
def getSQLcmnds(rowlist):
    cmdlist = []
    for row in rowlist:
        valstr = row2vals(row)
        cmd = f"INSERT INTO {TableName} VALUES ({valstr});"
        cmdlist.append(cmd)
    return cmdlist

# connect to the database
def dbconnect():
    connection = psycopg2.connect(
        host="localhost",
        database=DBname,
        user=DBuser,
        password=DBpwd,
    )
    # connection.autocommit = True
    return connection

# create the target table 
# assumes that conn is a valid, open connection to a Postgres database
def createTable(conn):

    with conn.cursor() as cursor:
        cursor.execute(f"""
            DROP TABLE IF EXISTS {TableName};
            CREATE TABLE {TableName} (
                TractId             NUMERIC,
                State               TEXT,
                County              TEXT,
                TotalPop            INTEGER,
                Men                 INTEGER,
                Women               INTEGER,
                Hispanic            DECIMAL,
                White               DECIMAL,
                Black               DECIMAL,
                Native              DECIMAL,
                Asian               DECIMAL,
                Pacific             DECIMAL,
                VotingAgeCitizen    DECIMAL,
                Income              DECIMAL,
                IncomeErr           DECIMAL,
                IncomePerCap        DECIMAL,
                IncomePerCapErr     DECIMAL,
                Poverty             DECIMAL,
                ChildPoverty        DECIMAL,
                Professional        DECIMAL,
                Service             DECIMAL,
                Office              DECIMAL,
                Construction        DECIMAL,
                Production          DECIMAL,
                Drive               DECIMAL,
                Carpool             DECIMAL,
                Transit             DECIMAL,
                Walk                DECIMAL,
                OtherTransp         DECIMAL,
                WorkAtHome          DECIMAL,
                MeanCommute         DECIMAL,
                Employed            INTEGER,
                PrivateWork         DECIMAL,
                PublicWork          DECIMAL,
                SelfEmployed        DECIMAL,
                FamilyWork          DECIMAL,
                Unemployment        DECIMAL
            );    
        """)

        print(f"Created {TableName}")

def add_constraints_indexes(conn):
    print("Executing constraints/index...")
    with conn.cursor() as cursor:
        cursor.execute(f"""
            ALTER TABLE {TableName} ADD PRIMARY KEY (TractId);
            CREATE INDEX idx_{TableName}_State ON {TableName}(State);
        """)

def load(conn, icmdlist):

    with conn.cursor() as cursor:
        print(f"Loading {len(icmdlist)} rows")
        start = time.perf_counter()
    
        for cmd in icmdlist:
            cursor.execute(cmd)

        elapsed = time.perf_counter() - start
        print(f'Finished Loading. Elapsed Time: {elapsed:0.4} seconds')

def run_queries(conn):
	with conn.cursor() as cursor:
		print("\nRunning summary queries...\n")

		cursor.execute("SELECT COUNT(DISTINCT state) FROM censusdata;")
		state_count = cursor.fetchone()[0]
		print(f"Distinct states: {state_count}")

		cursor.execute("SELECT COUNT(DISTINCT county) FROM censusdata WHERE state = 'Oregon';")
		oregon_counties = cursor.fetchone()[0]
		print(f"Distinct counties in Oregon: {oregon_counties}")

		cursor.execute("SELECT COUNT(DISTINCT county) FROM censusdata WHERE state = 'Iowa';")
		iowa_counties = cursor.fetchone()[0]
		print(f"Distinct counties in Iowa: {iowa_counties}")

def copy_load(conn, rowlist):
	import io

	print(f"Using COPY to load {len(rowlist)} rows")
	start = time.perf_counter()

	# Create in-memory text stream like a CSV file
	data_stream = io.StringIO()
	for row in rowlist:
		for key in row:
			if not row[key]:
				row[key] = '0'  # handle nulls as 0
			row['County'] = row['County'].replace("'", "")  # clean quotes

		values = [
			row['TractId'],
			row['State'],
			row['County'],
			row['TotalPop'],
			row['Men'],
			row['Women'],
			row['Hispanic'],
			row['White'],
			row['Black'],
			row['Native'],
			row['Asian'],
			row['Pacific'],
			row['VotingAgeCitizen'],
			row['Income'],
			row['IncomeErr'],
			row['IncomePerCap'],
			row['IncomePerCapErr'],
			row['Poverty'],
			row['ChildPoverty'],
			row['Professional'],
			row['Service'],
			row['Office'],
			row['Construction'],
			row['Production'],
			row['Drive'],
			row['Carpool'],
			row['Transit'],
			row['Walk'],
			row['OtherTransp'],
			row['WorkAtHome'],
			row['MeanCommute'],
			row['Employed'],
			row['PrivateWork'],
			row['PublicWork'],
			row['SelfEmployed'],
			row['FamilyWork'],
			row['Unemployment'],
		]
		data_stream.write('\t'.join(map(str, values)) + '\n')

	data_stream.seek(0)

	with conn.cursor() as cursor:
		cursor.copy_from(data_stream, TableName, sep='\t', null='')

	elapsed = time.perf_counter() - start
	print(f'COPY complete. Elapsed Time: {elapsed:0.4f} seconds')



def main():
    initialize()
    conn = dbconnect()
    rlis = readdata(Datafile)
    #cmdlist = getSQLcmnds(rlis)

    if CreateDB:
        createTable(conn)

    #load(conn, cmdlist)
    copy_load(conn, rlis)

    if CreateDB:
        add_constraints_indexes(conn)

    run_queries(conn)

if __name__ == "__main__":
    main()



