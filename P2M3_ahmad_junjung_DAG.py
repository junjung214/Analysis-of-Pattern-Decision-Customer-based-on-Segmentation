'''
=================================================
Milestone 3

Nama  : Ahmad Junjung S
Batch : FTDS-033-RMT

Program ini dibuat untuk melakukan automasi pengambilan data dari postgress server docker lalu di cleaning setalh itu post ke elastic yang akan digunakan untuk analisa terhadap Data yang telah dibersihkan di Elastic nantinya
=================================================
'''

import datetime as dt
from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from Load_Data import LoadData
from Post_Data import PostData
from Cleaning_Data import CleaningData

default_args = {
    'owner': 'somad',
    'start_date': dt.datetime(2024, 8, 18, 10, 15, 0) - dt.timedelta(hours=7),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=1),
}

with DAG('M3_Pipline',
         default_args=default_args,
         #schedule_interval=timedelta(minutes=5),        #cara 1 minimal menit
         #schedule_interval='@daily'                     #cara 2 minimal jam
         schedule_interval= '30 6 * * *',                 # setup untuk setiap hari di jamm 6.30 pagi
         catchup=False
         ) as dag:

    #task 1
    load_data = PythonOperator(
        task_id = 'Load_Data_From_Postgress',
        python_callable = LoadData
    )

    #task 2
    clean_data = PythonOperator(
        task_id = 'Cleaning_Data',
        python_callable = CleaningData
    )

    #task 3
    post_data = PythonOperator(
        task_id = 'Post_To_Elastic',
        python_callable = PostData
    )

load_data >> clean_data >> post_data 

'''
SC untuk Load_Data :

import pandas as pd
import psycopg2 as db

def LoadData():
    ''''''
    Fungsi ini untuk load data dari postgress dengan format : 
    connection : "dbname='airflow' host='postgres' user='airflow' password='airflow' port='5432'"
    Read Data : 
    pd.read_sql(your_file, conection)
    Save Data : 
    df.to_csv(your_file)
    ''''''
    conn_string="dbname='airflow' host='postgres' user='airflow' password='airflow' port='5432'"
    conn=db.connect(conn_string)
    df=pd.read_sql("select * from table_m3", conn)
    df.to_csv('/opt/airflow/dags/P2M3_ahmad_junjung_data_raw.csv')
'''

'''
SC Untuk Cleaning_Data : 

import pandas as pd

def CleaningData():
    ''''''
    Fungsi ini digunakan untuk cleaning data dari data yang tersedia di lokal
    Read Data : 
    df=pd.read_csv(your_file)
    Cleaning Data:
    df.drop_diplicates()
    df.columns = df.columns.str.lower()  
    df.columns = df.columns.str.replace( , '_')   
    df.columns = df.columns.str.replace('[^\w]', '', regex=True)
    df.drop_duplicates
    df.dropna()
    Save Data to Clean : 
    df.to)csv(your_file)
    ''''''

    df = pd.read_csv('/opt/airflow/dags/P2M3_ahmad_junjung_data_raw.csv')
    #case pertama drop duplikasi data kecuali kolom id dan baris dimana hal ini pasti tidak akan punya diplikasi data
    df.drop_duplicates(subset=['Year_Birth', 'Education', 'Marital_Status',
        'Income', 'Kidhome', 'Teenhome', 'Dt_Customer', 'Recency', 'MntWines',
        'MntFruits', 'MntMeatProducts', 'MntFishProducts', 'MntSweetProducts',
        'MntGoldProds', 'NumDealsPurchases', 'NumWebPurchases',
        'NumCatalogPurchases', 'NumStorePurchases', 'NumWebVisitsMonth',
        'Response', 'Complain'], inplace=True)
    #normalisasi kolom : 
    df.columns = df.columns.str.lower()  # Mengubah semua nama kolom menjadi lowercase
    df.columns = df.columns.str.replace(' ', '_')  # Mengganti spasi dengan underscore
    df.columns = df.columns.str.replace('[^\w]', '', regex=True)  # Menghapus spasi/tab/simbol yang tidak diperlukan
    #Handling missing value dalam kasus ini akan memilih untuk di drop karena hanya 24 data saja dan ini bukan MAR karena tidak ada ketergantunggan data yang hilang dengan kolom lainnya
    df.dropna(inplace=True)
    df.to_csv('/opt/airflow/dags/P2M3_ahmad_junjung_data_clean.csv') 
'''

'''
SC untuk Post_Data: 

import pandas as pd
from elasticsearch import Elasticsearch

def PostData():
    ''''''
    Fungsi ini untuk post data ke Elastic Search 

    Connection Elastic : 
    es = ElasticSearch(port)
    Read Data : 
    pd.read_csv(your_data)
    Post Data : 
    for i,r in df.iterrows():
        doc=r.to_json()
        res=es.index(index="m3_dataset", doc_type="doc", body=doc)
    ''''''
    es = Elasticsearch("http://elasticsearch:9200") 
    df=pd.read_csv('/opt/airflow/dags/P2M3_ahmad_junjung_data_clean.csv')
    for i,r in df.iterrows():
        doc=r.to_json()
        res=es.index(index="data_m3", doc_type="doc", body=doc)
'''
