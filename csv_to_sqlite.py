# Alexa Witkin
# CS 2500

import sqlite3 # included in standard python distribution
import pandas as pd

# create new database
con = sqlite3.connect('mountain_data.db')
cur = con.cursor()

# load customers.csv into database
cur.execute("DROP TABLE IF EXISTS Customers;")
users = pd.read_csv('customers.csv')
users.to_sql('Customers', con, if_exists='replace')

# load plates.csv into database
cur.execute("DROP TABLE IF EXISTS Plates;")
users = pd.read_csv('plates.csv')
users.to_sql('Plates', con, if_exists='replace')

# load liveData.csv into database
cur.execute("DROP TABLE IF EXISTS LiveData;")
users = pd.read_csv('liveData.csv')
users.to_sql('LiveData', con, if_exists='replace')


con.commit()