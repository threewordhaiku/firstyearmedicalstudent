from . import AppCursor, DB_URL
from sqlalchemy import create_engine
import pandas as pd


def fetch_table(table_name):
    """Fetches all rows from the given table_name

    Args:
        table_name: Name of the table to fetch from.

    Returns:
        List of table headers and rows extracted from DictResult.
    """
    with AppCursor() as cur:
        cur.execute("SELECT * FROM {}".format(table_name))
        return [[col.name for col in cur.description]] + [row for row in cur]


def download_table(table_name, csv_joinstr='|'):
    """Gets the given table_name as a CSV-ready string.

    Args:
        table_name: Name of the table to download as a string.

        csv_joinstr: Delimiter token for the CSV file.
                     Default: '|' (single pipe)
    
    Returns:
        String ready to be dumped into a CSV file.
        First line of string contains table headers.
    """
    #Create a list to store table values, including table name and headers
    #table name
    output_strs = [table_name]

    #Query DB for selected table via cursor
    sql = """SELECT * FROM {};""".format(table_name)
    with AppCursor() as cur:
        cur.execute(sql)
    
        #table headers
        table_heads = [col.name for col in cur.description]
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
    #Skip first 2 rows; they are table name and header row
    csv_data = pd.read_csv(csv, delimiter='|', skiprows=1, header=0)
    
    #Insert Dataframe to sql
    #If table exists, drop it. Cascade option drops foreign key dependents.
    with AppCursor() as cur:
        cur.execute("DROP TABLE IF EXISTS {} CASCADE;".format(table_name))

    #Recreate table, and insert data. Create if does not exist.
    csv_data.to_sql(table_name, engine, index=False)
    return


