# snips_api

*A module for writing Snippets to the database*

## Contents

**[Usage](#usage) |**
**[Requirements](#requirements) |**
**[Parser](#parser) |**
**[API](#api) |**
**[Utilities](#utilities) |**
**[Other files](#other-files)**

**Todo**

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



# Parser

**Jump to formatting for: **
**[Directives] |**
**[Snippets] |**
**[Choices] |**
**[Flag operations] |**
**[Sample file](../misc_files/sample_parser_text.txt) |**


The snips_parser submodule offers a single `parse()` function, which is 
intended to be its sole entry point. The parser simplifies the process for
feeding snippets and choices to the database mainly by making data 
representation less cumbersome and more intuitive.

The `parse()` function takes the specially-formatted text as its single 
string argument and will raise a `ParserError` if there are any problems with 
the input text. If all goes well, the function then returns a generator that 
yields (query, data) tuples for execution to the database.


The role of each line in your input text is inferred from how they are 
formatted. There are a total of four roles: [directives], [snippets], 
[choices] and [flag operations]. An example of the formatted text input can 
be found in this file: 
[`sample_parser_text.txt`](../misc_files/sample_parser_text.txt). 
For details on formatting, follow the links above for each role to their 
respective subsections below.

To use the parser, you must provide the text, and then execute the `parse()` 
function's output to the database:

```py
# This script should be placed at the same directory level as webapp.py
from snips_api import snips_parser as sp
from db_tools import QuickCursor

with open('misc_files/sample_parser_text.txt', 'r') as f:
    text = f.read()

with QuickCursor() as cur:
    for sql, data in snips_parser.parse(text):
        cur.execute(sql, data)
```

## Formatting directives

Directives contain meta-information about your input. They must appear 
together at the top of your text.  These are the available directives:

directive | argument | dependencies | compulsory | description |
--------- |:--------:|:------------:|:----------:| ----------- |
ROOT_SNIP_ID | int   | -            | YES        | Indicates the snip_id of the first snippet.
COMMENT_MARKER | str | -            | -          | Indicates the inline comment character(s). If not declared, comments will be treated as actual input.
REF_NUMS_ARE_SNIP_IDS | - | -       | -          | Makes the reference numbers provided for each snippet become their snip_ids in the database.
OVERWRITE_DB_SNIP_IDS | - | REF_NUMS_ARE_SNIP_IDS | - | Makes the reference numbers provided for each snippet overwrite existing snip_ids in the database.

Only one directive may be declared per line. The line must not begin with any 
indent, and must start with `directive:`. Arguments are delimited by a single
space. If you declare a directive without its dependencies, a ParserError will
be raised.

Here is an example of declaring directives:

```
directive:ROOT_SNIP_ID 456
directive:COMMENT_MARKER //
directive:REF_NUMS_ARE_SNIP_IDS
directive:OVERWRITE_DB_SNIP_IDS
```

## Formatting snippets

In your input text, snippets are indexed using *reference numbers*, which help
you to maintain references to your snippets until it's time to assign them 
snip_ids. 

Lines that define snippets must not be indented and must contain a
reference number unique within each document containing your input. If you are
passing string literals into the [`parse()`](#parser) function, the reference
number must be unique within the string. Reference numbers can be surrounded 
by any kind of symbol(s).

You can force snippet reference numbers to be used as snip_ids using the 
`REF_NUMS_ARE_SNIP_IDS` [directive].

Here is an example of how snippets are formatted. Note that while there are no
restrictions on how the reference numbers are enclosed, I recommend picking a
style and sticking to it consistently.

```
28. Introducing myself, I took a chair and sat beside John.
    (some choice goes here)
29. John: “Ah, doctor. Not too good…”
    (another choice goes here)
```

## Formatting choices

Because the originate from [snippets], choices must be placed immediately 
after the snippet they 'originate' from. They must be indented (any amount of 
whitespace will count), and those belonging to the same snippet must be at the 
same indent level (like in Python).

Choices must each have a label (compulsory) and a 'target' snippet that they 
link to (explicitly or implicitly defined).

To explicitly specify a snippet, place a `->` after the label text, followed 
by the snippet's reference number. If you do not indicate the target snippet
(meaning you do not have the `->` and a reference number), the choice will
link to the next immediate snippet that follows.

Below is an example of how choices are formatted -- in the example, the 
"So, John..." option implicitly points to snippet 29 below it, while the  
"looking good" option explicitly points to snippet 30.

Note that while there are no restrictions on how the reference numbers are 
enclosed, I recommend picking a style and sticking to it consistently.
```
28. (some snippet text here)
    “So, John, how are you feeling today?”
    “You’re looking good today.” -> 30
29. (yeahhh more snippet text)
    “I mean, you look great today!” -> 33
```

## Formatting flag operations

Flag operations that use expressions for checking and modifying flag states 
follow the same indentation rules as [choices], except they have have to be 
indented more deeply than the choices they are applicable for. 

There's not a lot to say about these expressions. Make sure flag names are 
valid (regex: `[_\w]+`), have a space in between flag name, operator and
value, make sure your operator is valid in Python.

Here's an example:
```
(28) (some snippet text here)
    (some choice)
        Requires skin_thickness >= 5
        johndoe_death = 1
        patient_deaths += 1
```

[directives](#formatting-directives)
[snippets](#formatting-snippets)
[choices](#formatting-choices)
[flag operations](#formatting-flag-operations)

# API

**Jump to: **
**[Snippet class](#snippet) |**
**[Choice class](#choice) |**
**[Other classes](#others) |**
**[Example](#api-usage-example)**

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

## API usage example

```py
# This script should be placed at the same directory level as webapp.py
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

---

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



