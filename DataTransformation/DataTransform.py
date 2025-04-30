import pandas as pd
import re
from datetime import timedelta

def main():
    df = pd.read_csv("bc_veh4223_230215.csv",
                    usecols=[
                            'EVENT_NO_TRIP', 'OPD_DATE',
                            'VEHICLE_ID', 'METERS', 'ACT_TIME',
                            'GPS_LONGITUDE', 'GPS_LATITUDE'
                            ])
    df.columns = df.columns.str.strip()

    print()

    print(f"Data Count: {len(df)}")

    # print(f"Columns: {df.shape[1]}")
    #df = df.drop(['EVENT_NO_STOP', 'GPS_SATELLITES', 'GPS_HDOP'], axis=1)
    #print(f"After Columns: {df.shape[1]}")

    df['TIMESTAMP'] = df.apply(convert_trimet_time, axis=1)
    df = df.drop(columns=['OPD_DATE', 'ACT_TIME'])

    df['dMETERS'] = df.groupby('EVENT_NO_TRIP')['METERS'].diff()
    df['dTIMESTAMP'] = df.groupby('EVENT_NO_TRIP')['TIMESTAMP'].diff()
    df['SPEED'] = df.apply(lambda row: row['dMETERS'] / row['dTIMESTAMP'].total_seconds(), axis=1)
    df = df.drop(columns=['dMETERS', 'dTIMESTAMP'])

    # for _, row in df.iterrows():
    #     print(row['TIMESTAMP'])
    print(df)
    max_row = df.loc[df['SPEED'].idxmax()]
    print(f"MAX SPEED: {max_row['SPEED']}")
    print(f"WHERE: {max_row['GPS_LONGITUDE']}, {max_row['GPS_LATITUDE']}")
    print(f"WHEN: {max_row['TIMESTAMP']}")
    print(f"MEDIAN SPEED: {df['SPEED'].median()}")
    print()

def convert_trimet_time(row):
    date = pd.to_datetime(row['OPD_DATE'], format='%d%b%Y:%H:%M:%S')
    time_delta = timedelta(seconds=row['ACT_TIME'])    
    return date + time_delta


if __name__ == "__main__":
    main()