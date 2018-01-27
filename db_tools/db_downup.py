from . import AppCursor, DB_URL
from sqlalchemy import create_engine
import pandas as pd

from collections import defaultdict


class DatabaseError(Exception):
    """Basic exception for errors raised by database"""
    def __init__(self, choice, msg=None):
        if msg is None:
            msg = "An error occured with database."
        super(DatabaseError, self).__init__(msg)



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
    csv_data = pd.read_csv(csv, delimiter='|', skiprows=2)
    
    #Insert Dataframe to sql
    #If table exists, drop it. Cascade option drops foreign key dependents.
    with AppCursor() as cur:
        cur.execute("DROP TABLE IF EXISTS {} CASCADE;".format(table_name))

    #Recreate table, and insert data. Create if does not exist.
    csv_data.to_sql(table_name, engine, if_exists='replace')
    return

def load_snippets(snip_id):
    """Queries database for game text

    Args:
        snip_id: the identification number for the respective snippet

    Returns:
        game_text as string
    """
    #Query DB for selected table via cursor
    sql = "SELECT * FROM snippets where snip_id = {};".format(snip_id)

    with AppCursor() as cur:
        rows = cur.execute(sql)
    
    if not rows:
        msg = "No rows in table `snippets` where snip_id = {}".format(snip_id)
        raise DatabaseError(msg)

    return output


def load_choices(snip_id, game_state):
    """Queries database for choices based on snip_id

    Args:
        snip_id: the identification number for the respective snippet
        game_state: dictionary representing game_state

    Returns:
        a list of dictionaries where each dictionary has the following structure:
            choice_data = {
                label: 'next',
                next: '123',
                mod_flags = [
                    'f1 += 1',
                    'f2 -= 1'
                ]
            }
    """
    #Query DB for selected table via cursor
    sql = "SELECT * FROM choices where snip_id = {};".format(snip_id)
    with AppCursor() as cur:
        rows = cur.execute(sql)
    
    # Figure out what rows to show
    rows_to_show = []
    for row in rows:
        # Collect conditions we need to check against
        condition_expressions = [expr
                                 for header, expr in row.items() 
                                 if 'check_flg' in header]
        # Proceed to next row if no conditions to check:
        if not condition_expressions:
            rows_to_show.append(row)
            continue

        # if there are condition, check them here
        for expr in condition_expressions:
            flag, operator, value = expr.split()
            flag_val = game_state.get(flag, 0)
            show_to_player = False
            exec('show_to_player = {flag_val} {operator} {value}'.format(**locals()))
            if not show_to_player:
                # if any of the conditions fail, don't bother checking the rest of the conditions
                break
        # if none of the conditions are broken, then we show this row
        else:
            rows_to_show.append(row)

    # put only stuff we want to show into the output list
    output = []
    for row in rows_to_show:
        # choice_data = {
        #     label: 'next',
        #     next: '123',
        #     mod_flags = [
        #         'f1 += 1',
        #         'f2 -= 1'
        #     ]
        # }

        choice_data = dict()
        choice_data['choice_label'] = row['choice_label']
        choice_data['next_snip_id'] = row['next_snip_id']
        choice_data['mod_flags'] = []

        for header, action in row.items():
            if 'mod_flg' in header:
                choice_data['mod_flags'].append(action)

        output.append(choice_data)

    return output


