# snips_api

*A module for writing Snippets to the database*

### Contents

**[Usage](#usage) |**
**[Requirements](#requirements) |**
**[Sample usage](#sample) |**
**[API documentation](#api) |**
**[Other files](#other-files)**

### Todo

- Update readme to cover the `snips_parser`



# Usage
This module is intended to be used as a scriptable interface for the database.
The module is currently functioning, but still in testing for use with the 
main game app.

# Requirements
You should know [how to define your `DATABASE_URL` environment variable][1] 
to point to the database that you intend to insert the snippets into. Database 
access is necessary for automatic assignment of snip_ids to your snippets. 

The database connection will only be created the first time you call 
[Snippet.generate_chain_sql()](#snippet). You do not need the database 
connection if you do not intend to commit your snippets to the database.

[1]: https://trello.com/c/rzDEieoG/70-heroku-app-deployment-steps


# Sample

```py
from snips_api import Snippet, RootSnippet

# Make some snippets:
s_start = RootSnippet(9000, 'Dr. Smith: "Okay, last question. If a runaway train is bearing down--"')
s_nointerrupt = Snippet('Dr. Smith: "--well, actually, I think you know the rest of it. What do you think?"')
s_nointerrupt2 = Snippet('Dr. Smith: "Hmm, I see. Alright, that\'s all for today. Thanks for coming down."')
s_interrupted = Snippet('Dr. Smith: "Oh. I see. Well then, I think that\'s all for today."')
end = TerminalSnippet('That was a strange interview...')

# The RootSnippet and TerminalSnippet are basically special cases of Snippets.
# Imagine that the Snippets form a tree starting from the RootSnippet and
# ending at the branch tips with TerminalSnippets.

# Add some choices to the snippets. Choices 'connect' snippets.
s_start.add_choice(
    "(You've heard this one before...)",
    next_snippet=s_nointerrupt)

# We can describe how the choice affects various game flags:
s_nointerrupt.add_choice(
    "I won't do anything",
    next_snippet=s_nointerrupt2
        ).add_modifies_flag('tut_switch_track = 0')
s_nointerrupt.add_choice(
    "I'd switch the tracks",
    next_snippet=s_nointerrupt2
        ).add_modifies_flag('tut_switch_track = 1')

# The add_check_flag defines conditions for the choice to be selectable.
# Both add_check and add_modifies methods return their Choice instance,
# so you can chain these methods together for readability, as shown here.
s_start.add_choice(
    "I won't do anything.",
    next_snippet=s_interrupted
        ).add_check_flag(
            'skin_thickness >= 5'
        ).add_modifies_flag(
            'tut_board_annoyed += 1'
        ).add_modifies_flag(
            'tut_switch_track = 0')

s_nointerrupt2.add_choice(
  '(Leave)',
  next_snippet=end)
s_interrupted.add_choice(
  '(Leave)',
  next_snippet=end)
```

# API
**Jump to: [Snippet](#snippet) | [Choice](#choice) | [Others](#others)**

>Note: all items in snips_api.components can be directly imported from the
>base snips_api module.

## Snippet

```
class snips_api.components.Snippet(text, snip_id=None)
  The Snippet is a basic container to hold the primary game text that carries
  the main plot of the game. Each Snippet minimally contains game text and a
  snip_id. The snip_id uniquely identifies it to other components in the game,
  such as Choices, which are created using Snippet.add_choice().

  Args:
    text    -- String representing game text. Supports UTF-8.
    snip_id -- Integer snip_id that uniquely identifies the snippet to other 
               game components. Compulsory for first snippet, if committing 
               snippets to database.

  Attributes:
    text    -- As above.
    snip_id -- As above.
    choices -- List of Choices leading out of the snippet

  Methods:
    set_snip_id(snip_id)
      Sets this snippet's snip_id to the given integer. Will raise
      CannotRedefineSnipIDError if this snippet's snip_id is no longer 
      'pending'.
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
      integer snip_id. If no snip_id is provided, defaults to use this
      snippet's existing snip_id. Raises SnippetError if no valid snip_id is 
      provided or found.
        Returns a tuple (sql_query, data) that can be unpacked into 
        AppCursor.execute().

    generate_chain_sql(insert_method='timid')
      Connects to database and generates (sql_query, data) pairs for use with
      AppCursor.execute(). This method imports from db_tools and thus requires
      a database connection defined in the DATABASE_URL environment variable
      so that 'pending' snip_ids can be resolved into snip_ids.

      The insert_method argument controls whether existing snip_ids in the 
      database should be overwritten ('rough' if yes, 'timid' if not).
      
      Raises TimidError when attempting to overwrite existing snip_ids. Raises
      CompilerError if any other errors happen while generating statements.
        Returns a generator object that yields two arguments for use with
        AppCursor.execute()
```

## Choice

```
class snips_api.components.Choice(label, next_snippet)
  The Choice links snippets together. Essentially, it represents a button with
  a label on it that takes the player to the target snippet when it's clicked.

  Args:
    label        -- String representing text on the button.
    next_snippet -- Represents the target snippet to take the player to when
                    this choice is selected. Can be any value, but is usually 
                    a Snippet object. See the Attributes section for details.

  Attributes:
    label          -- As above.
    next_snippet   -- Must be Snippet object for Snippet.generate_chain_sql() 
                      to work. In the snips_api.snips_parser module, the 
                      "snippet reference number" was stored here as a 
                      temporary proxy for a Snippet object.
    from_snip      -- Represents the 'origin' snippet this Choice belongs to.
                      Can be any value, but is usually a Snippet object. Can 
                      be practically applied in the same manner as the 
                      next_snippet attribute.
    check_flags    -- List of flags to check against to determine if the 
                      Choice will be shown to the player.
    modifies_flags -- List of flag modifications the Choice will make if the
                      player selects it.
  
  Methods:
    set_source_snip(snip)
      Updates the next_snippet attribute with the given value.

    add_check_flag(expression)
      Adds a condition for whether the Choice will be shown to the player.
      The given `expression` must be a valid Python comparison expression as a
      string. Relies on parse_expression() -- see below.
        Returns the Choice instance (`self`).

    add_modifies_flag(expression)
      Adds a flag modification that occurs if the player selects the Choice.
      The given `expression` must be a valid Python assignment expression as a
      string. Relies on parse_expression() -- see below.
        Returns the Choice instance (`self`).

    parse_expression(expr, use_symbols='comparison')
      Checks if the expression is valid. Also checks if the flag(s) involved
      are valid. The use_symbols argument can be 'comparison' or 'assignment'.
      Raises BadExpressionError.
        Returns a boolean.

    ensure_valid_flag_name(flag_name)
      Checks if the given string is a valid flag name. Raises 
      BadExpressionError if the string is invalid.
        Returns nothing.

    ensure_valid_operator(oper, symbol_set)
      Checks if the given string is a valid operator for the given kind of
      symbol_set. The symbol_set argument can be 'comparison' or 'assignment'.
      Rauses BadExpressionError if the operator is invalid.
        Returns nothing.
```


## Others

```
class snips_api.components.RootSnippet(Snippet)
  This subclass is similar to its Snippet parent class, but must be 
  initialized with an integer snip_id argument.


class snips_api.components.TerminalSnippet(Snippet)
  This subclass is similar to its Snippet parent class, but choices cannot be
  added to it.

  Methods:
    add_choice(*args, **kwargs)
      Overwrites the parent method to raise TerminalSnippetError.
```


# Other files

**components.py**
>Contains the class definitions. You should import the classes from the main 
>module instead. (i.e. from snips_api import *)


**compiler.py**
>Contains functions for inferencing snip_ids and generating SQL statements
>for inserting and updating rows.


**exceptions.py**
>Custom exceptions.


**readme.md**
>This file.
