from . import Cursor, DB_URL
from sqlalchemy import create_engine
import pandas as pd


def fetch_table(table_name):
    """Fetches all rows from the given table_name

    Args:
        table_name: Name of the table to download as a string.

    Returns:
        DictCursor containing query results.
    """
    with Cursor("SELECT * FROM {}".format(table_name)) as cur:
        return cur


def download_table(table_name, csv_joinstr='|'):
    """Gets the given table_name as a CSV-ready string.

    Args:
        table_name: Name of the table to download as a string.

        csv_joinstr: Delimiter token for the CSV file.
                     Default: '|' (single pipe)
    
    Returns:
        String ready to be dumped into a CSV file
    """
    #Create a list to store table values, including table name and headers
    #table name
    output_strs = [table_name]

    #Query DB for selected table via cursor
    sql = """SELECT * FROM {};""".format(table_name)
    with Cursor() as cur:
        cur.execute(sql)
    
        #table headers
        table_heads = [desc[0] for desc in cur.description]
        output_strs.append(
            csv_joinstr.join(table_heads)
        )

        #table data
        for row in cur:
            output_strs.append(
                csv_joinstr.join(str(cell) for cell in row)
            )

    #returns the output string list joined by \n
    return '\n'.join(output_strs)
    #.js will package to a csv file and push to client (To be done)


def upload_table(table_name, csv):
    """Uploads a CSV file into the given table, replacing existing data.
    
    Args:
        table_name: String identifying the table to overwrite.

        csv: File-like object containing the csv file.

    Returns:
        None
    """
    #Create a connection to the database
    engine = create_engine(DB_URL)
    #Reads the csv file to a pandas dataframe
    csv_data = pd.read_csv(csv)
    
    #Insert Dataframe to sql
    #If table exists, drop it, recreate it, and insert data. Create if does not exist.
    csv_data.to_sql(table_name, engine, if_exists='replace')
    return


