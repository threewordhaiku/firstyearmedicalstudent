///////////////////////////////////////////////////////////
//  snips_api - module for writing Snippets to database  //
///////////////////////////////////////////////////////////

// Usage
This module is intended to be used as a scriptable interface for the database. 
The interfaces here are (currently) not meant for use with the main game app.

// Requirements
You should know how to define your DATABASE_URL environment variable to point 
to the database that you intend to insert the snippets into. Database access 
is necessary for automatic assignment of snip_ids to your snippets. 

The database connection will only be created the first time you call 
Snippet.generate_chain_sql(). You do not need the database connection if you 
do not intend to commit your snippets to the database.


///////////////////////////////////////////////////////////
//  Sample usage                                         //
///////////////////////////////////////////////////////////

from snips_api import Snippet

# Make a few new snippets
new_snippet = Snippet('Alice was beginning to get very tired of sitting by '
                      'her sister on the bank...')
snip_rabbit = Snippet('...when suddenly a White Rabbit with pink eyes ran '
                      'close by her.')

# Add some choices; for simplicity, both choices lead to the same snippet
new_snippet.add_choice('Take a nap', next_snippet=snip_rabbit)
dc = new_snippet.add_choice('Make a daisy-chain', next_snippet=snip_rabbit)

# Let the daisy-chain choice only be available when the "motivation" flag 
# is greater than 0
dc.add_check_flag('motivation > 0')

# If this choice is picked, increment the "daisy_chains" flag by 1
dc.add_modifies_flag('daisy_chains += 1')

# If we want to commit our snippets to the database, the 'root' snippet must
# have a snip_id defined, so the module can infer where subsequent snip_ids 
# should start counting up from
new_snippet.set_snip_id(1)
from db_tools import AppCursor
with AppCursor() as cur:
    # We use the 'rough' argument to overwrite any rows that have snip_id = 1
    # Since we did not define a snip_id for our second snippet, it will be
    # assigned an unused snip_id instead
    for sql, data in new_snippet.generate_chain_sql(insert_method='rough'):
        print('QUERY:', sql)
        print('DATA: ', data)
        cur.execute(sql, data)


///////////////////////////////////////////////////////////
//  Main module contents                                 //
///////////////////////////////////////////////////////////

// Note: all items in snips_api.components can be directly imported from
// the base snips_api module.

class snips_api.components.Snippet(text, snip_id=None)
  The Snippet is the basic component to contain the primary game text that 
  carries the main plot of the game. Each Snippet minimally contains game text 
  and a snip_id. The snip_id uniquely identifies it to other components in the 
  game, such as [Choices](#snips_api.components.choice), which are created 
  with the Snippet.add_choice() method.

  Args:
    text -- Game text. Commits into database under the `game_text` column in
            the `snippets` table.
    snip_id -- Unique integer snip_id that identifies the snippet to other 
               game components. Compulsory for first snippet, if committing 
               snippets to database.

  Attributes:
    text     -- game text
    snip_id  -- unique integer identifier
    choices  -- list of choices leading out of the snippet

  Methods:
    set_snip_id(snip_id)
      Sets this snippet's snip_id to the given integer. Will raise
      CannotRedefineSnipID if this snippet's snip_id is no longer 'pending'.
        Returns nothing.

    add_choice(*args, **kwargs)
      Creates a choice using the given arguments and binds the choice to this 
      snippet. 
        Returns a Choice object.

    get_snippets_tree()
      Finds all snippets 'reachable' from this one via choices. The list
      starts with this snippet. Snippets in the list are unique. 
        Returns a list of Snippet objects.

    make_insert_args(use_snip_id=None)
      Creates an "INSERT INTO" SQL statement for this snippet with the given 
      snip_id. If no snip_id is provided, defaults to use this snippet's 
      snip_id. Raises SnippetError if no valid snip_id is provided or found.
        Returns a tuple (sql_query, data) that can be unpacked into 
        AppCursor.execute().

    generate_chain_sql(insert_method='timid')
      Connects to database and generates (sql_query, data) pairs for use with
      AppCursor.execute(). This method indirectly imports db_tools and thus 
      requires a database connection defined in the DATABASE_URL environment 
      variable so that 'pending' snip_ids can be resolved into snip_ids.

      The insert_method argument  controls whether existing snip_ids in the 
      database should be overwritten and can be can be 'timid' or 'rough'.
      
      Raises TimidError when attempting to overwrite existing snip_ids. Raises
      CompilerError if any other errors happen while generating statements.
        Returns a generator object that yields two arguments for use with
        AppCursor.execute()


class snips_api.components.RootSnippet(Snippet)
  This subclass is similar to its Snippet parent class, but must be 
  initialized with an integer snip_id argument.


class snips_api.components.TerminalSnippet(Snippet)
  This subclass is similar to its Snippet parent class, but choices cannot be
  added to it.

  Methods:
    add_choice(*args, **kwargs)
      Overwrites the parent method to raise TerminalSnippetError.


///////////////////////////////////////////////////////////
//  Other files in this module                           //
///////////////////////////////////////////////////////////

components.py
  Contains the class definitions. You should import the classes from the main 
  module instead. (i.e. from snips_api import *)

compiler.py
  Contains functions for inferencing snip_ids and generating SQL statements
  for inserting and updating rows.

exceptions.py
  Custom exceptions.

readme.txt
  This file.