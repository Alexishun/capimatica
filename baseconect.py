import pymysql
import pandas as pd
from sqlalchemy import create_engine
import os 
from dotenv import load_dotenv
load_dotenv()

# --- Crear motor SQLAlchemy ---
USER     = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST     = os.getenv("HOST")
PORT     = os.getenv("PORT")
DB       = os.getenv("DB")
conn_str = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
engine = create_engine(conn_str)


def align_to_hour(df):
    df = df.copy()
    df['x'] = pd.to_datetime(df['x'], utc=True).dt.floor('h')
    return df

lugar = 'lima'
df = pd.read_csv(f"bases en csv/{lugar} hum.csv")  
df1 = pd.read_csv(f"bases en csv/{lugar} precipitacion.csv")
df2 = pd.read_csv(f"bases en csv/{lugar} speed.csv")
df3= pd.read_csv(f"bases en csv/{lugar} temp.csv")
df4=pd.read_csv(f"bases en csv/{lugar} uv.csv")
df5=pd.read_csv(f"bases en csv/{lugar} sensacion.csv")

df  = align_to_hour(df)
df1 = align_to_hour(df1)
df2 = align_to_hour(df2)
df3 = align_to_hour(df3)
df4 = align_to_hour(df4)
df5 = align_to_hour(df5)

features_cusco = (
    df
    .merge(df1, on='x', suffixes=('_humedad', '_precipitacion'))
    .merge(df2, on='x', suffixes=('', '_speedwind'))
    .merge(df3, on='x', suffixes=('', '_temperatura'))
    .merge(df4, on='x', suffixes=('', '_radiacion'))
    .merge(df5, on='x', suffixes=('', '_sensacion'))
)
features_cusco=features_cusco.rename(columns={'x':'fecha_hora','y':'y_speedwind'})
print(features_cusco.head())
features_cusco=features_cusco[features_cusco['fecha_hora']>'2020-01-01 00:00:00+00:00']
features_cusco.to_sql(
    name='lima_feature',
    con=engine,
    if_exists='append', 
    index=False
)

# print(df1.head())

# print(df2.head())

# print(df3.head())

# print(df4.head())

# print(df5.head())

