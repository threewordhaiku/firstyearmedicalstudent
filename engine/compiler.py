from .exceptions import ConflictingSnipID
from db_tools import AppDBConnection, AppCursor


def snippet_chain_to_sql_data(snip, insert_method='timid'):
    snips = [snip] + snip.get_child_snippets()
    dict_id_to_snip = assign_ids(snips, insert_method)

    # `placeholders` is a list of n copies of '(%s, %s)' where n = len(snips)
    # They are placeholders for actual values that are merged into the query
    # when the query is executed to the database via psycopg2
    placeholders = ['(%s, %s)'] * len(snips)
    sql = """INSERT INTO snippets(snip_id, game_text) VALUES """
    sql += ', '.join(placeholders)
    
    # `values` is a flat (non-nested) list of values to merge into sql
    values = []
    for snip_id, snippet in dict_id_to_snip.items():
        values.append(snip_id)
        values.append(snippet.text)
    
    return sql, values


def assign_ids(snips, insert_method):
    """Matches snippets with target rows in database"""
    # Complain if first snippet has no snip_id to count up from
    try:
        root_id = int(snips[0].snip_id)
    except TypeError:
        raise CompilerError('first snippet in snippet stack has invalid '
                            'snip_id (expected int, got {})'
                           ).format(repr(snips[0].snip_id))

    # Complain if you don't insert it properly
    accept_methods = ['timid', 'rough']
    if insert_method not in accept_methods:
        raise CompilerError('unexpected insert_method option '
                            '(insertion must be "timid" or "rough", not "{}")'
                           ).format(insert_method)

    # Split the snips into 2 lists
    pending_snip_id = []   # snippets that snip.snip_id == 'pending'
    declared_snip_id = []  # snippets that snip.snip_id != 'pending'
    for snip in snips:
        if snip.snip_id != 'pending':
            declared_snip_id.append(snip)
        else:
            pending_snip_id.append(snip)
    
    # Complain if encountering resistance when timidly inserting
    if insert_method == 'timid':
        # Fetch rows that contain snip_ids in declared_snip_id
        for row in fetch_rows_with_snipids(
            [snippet.snip_id for snippet in declared_snip_id]
        ).values():
            # If rows exist, timidly abort
            if row:
                raise CompilerError('snip_id {} already exists in the '
                                    'database, "timid" insert method aborted'
                                   ).format(row['snip_id'])

    # If using rough insert, it doesn't matter if rows already exist among
    # the declared snip_ids, because we will overwrite those rows.
    # If we made it this far, just map all the snippets to a snip_id
    # (by finding spare snip_ids and using the declared snip_ids)

    # Find spare snip_ids for the snippets who are pending one
    spare_ids = find_spare_snipids(startfrom=root_id+1, 
                                   needed=len(pending_snip_id))

    # Map snip_ids to the snippets that will adopt them
    output = {}
    for snip_id, snippet in zip(spare_ids, pending_snip_id):
        output[snip_id] = snippet
    for snippet in declared_snip_id:
        output[snippet.snip_id] = snippet

    return output


def fetch_rows_with_snipids(list_snip_ids):
    """Finds out for each snip_id whether a record exists already

    Returns a dict of {snip_id: (row or None)}
    """
    output = {snip_id: None for snip_id in list_snip_ids}
    
    query = """SELECT * FROM snippets WHERE snip_id IN ({})"""
    placeholders = ['%s'] * len(list_snip_ids)
    query = query.format(', '.join(placeholders))
    with AppCursor() as cur:
        cur.execute(query, list_snip_ids)
        rows = cur.fetchall()
    
    existing_rows = {row['snip_id']: row for row in rows}
    output.update(existing_rows)
    return output


def find_spare_snipids(startfrom, needed):
    """Generates a list of spare snip_ids"""
    free_ids = []
    found = 0
    while found < needed:
        # Each loop defines a list of 100 candidate snip_ids
        candidate_snipids = list(range(startfrom, startfrom+100))

        # fetch_rows_with_snipids() returns a dict of {row['snip_id']: row}
        # Fetch rows that contain any of our candidates
        existing_snip_ids = [
            snip_id for snip_id, row in 
            fetch_rows_with_snipids(candidate_snipids).items()
            if row is not None
        ]

        # If none of the candidates exist in the db:
        if not existing_snip_ids:
            # Transfer as many snip_ids from candidate_snipids as we need/can
            for candidate in candidate_snipids:
                if found < needed:
                    free_ids.append(candidate)
                    found += 1
                else:
                    break
        
        # But if some candidates are already used in the db:
        else:
            # Remove existing snip_ids from candidate_snipids
            for i in existing_snip_ids:
                candidate_snipids.remove(i)

            # Transfer as many snip_ids from candidate_snipids as we need/can
            for candidate in candidate_snipids:
                if found < needed:
                    free_ids.append(candidate)
                    found += 1
                else:
                    break
        # For next loop in `while`, start from the next 100 candidates
        startfrom += 100
    
    # Once we're done finding candidates, do a SAN check
    assert(len(free_ids) == needed)
    return free_ids



class CompilerError(Exception):
    """Basic exception for errors raised by Snippets"""
    def __init__(self, hint=None):
        if hint is None:
            hint = ("An error occured while compiling snippets into the "
                    "database. No changes were committed.")
        super(SnippetError, self).__init__(hint)
