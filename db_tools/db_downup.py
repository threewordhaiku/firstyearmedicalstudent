from connections import Cursor, DB_URL
from sqlalchemy import create_engine
import pandas as pd

def download_table(table_name):

	#Query DB for selected table via cursor
	sql = ("""SELECT * FROM {};"""
		).format(
   			table_name
   			) 
	with Cursor() as cur:
	cur.execute(sql)

	#Create a list to store table values, including table name and headers
	#table name
	output_strs = [table_name]
	
	#table headers
	table_heads = [desc[0] for desc in cur.description]
	output_strs.append('|'.join(table_heads))

	#table data
	for row in cur:
		output_strs.append(
			'|'.join(str(cell) for cell in row)
		)

	#returns the output string list joined by \n
	return '\n'.join(output_strs)
	#.js will package to a csv file and push to client (To be done)


def upload_table(csv, table_name):
	#Create a connection to the database
	engine = create_engine(DB_URL)
	#Reads the csv file to a pandas dataframe
	csv_data = pd.read_csv(csv)
	
	#Insert Dataframe to sql
	#If table exists, drop it, recreate it, and insert data. Create if does not exist.
	csv_data.to_sql(table_name, engine, if_exists='replace')
	return


