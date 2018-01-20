"""
# snips_parser.py

This module contains functions to create SQL queries from plain text.
The main steps for this process are:
    0.  Parse text for directives that contain meta-information about the
        input text (e.g. comment symbols)

    1.  Parse text into independant Choices and Snippets (in that order). At
        At this stage, snippets are identified by a 'reference number', not by
        any snip_id.

    2.  Link choices to snippets by resolving reference numbers to the 
        associated Snippet object

    3.  Verify that all snippets are linkable (no 'orphaned' snippets, i.e.
        all snippets are reachable from the 'root snippet', the first snippet
        defined in the input text)

    4.  Generate and yield SQL, data pairs for execution into database
"""


import re

from .components import Choice, Snippet
from .exceptions import ParserError

DIRECTIVES = {
    # Must be in format DIRECTIVE_NAME: None or type_class
    'ROOT_SNIP_ID': int   # Compulsory
    ,'REF_NUMS_ARE_SNIP_IDS': None
    ,'OVERWRITE_DB_SNIP_IDS': None  # REF_NUMS_ARE_SNIP_IDS must be active too
    ,'COMMENT_MARKER': str
}
DIRECTIVE_ARG_SEPARATOR = ' '
DIRECTIVE_IDENT_STR = r'directive:'  # This is regex


def parse(text):
    """Takes a plaintext string and parses its contents into SQL statements

    Intended to be the entry-point to the module.
    This function bridges the conversion of Snippets to their (query, data)
    representation for execution to the database.
    """
    snippets, directives = parse_text(text)
    
    root_snip = snippets[min(snippets.keys())][0]
    root_snip.set_snip_id(directives['ROOT_SNIP_ID'])

    insert_method = 'timid'
    if directives.get('OVERWRITE_DB_SNIP_IDS', None):
        # Note: This directive also implies REF_NUMS_ARE_SNIP_IDS
        insert_method = 'rough'
    
    for sql, data in root_snip.generate_chain_sql(insert_method):
        yield sql, data 


def parse_text(text):
    """Converts text into snippets and directives."""
    textlines = text.strip().splitlines()
    textlines, directives = get_directives(textlines)
    
    first_line_num = get_ref_num(textlines[0])
    comment_marker = directives.get('COMMENT_MARKER', None)

    snippets = dict()

    # Ensure ref_nums in the text are unique
    parse_data = [(ref_num, game_text, choices)
                  for ref_num, game_text, choices
                  in interpret(textlines, comment_marker)]

    for ref_num, game_text, choices in parse_data:
        if ref_num in snippets:
            msg = ('Multiple snippets in your text have reference number {}'
                  ).format(ref_num)
            raise ParserError(msg)
        #print(game_text)
        snip = Snippet(game_text)
        if directives.get('REF_NUMS_ARE_SNIP_IDS', None):
            snip.set_snip_id(ref_num)
        snippets[ref_num] = (snip, choices)
        
    # Link up choices and snippet objects
    for snip, choices in snippets.values():
        for choice in choices:
            choice.set_source_snip(snip)
            snip.choices.append(choice)
            tgt_ref_num = choice.next_snippet
            if tgt_ref_num not in snippets:
                msg = ('Invalid snippet reference number {} for the choice '
                       '"{}"').format(tgt_ref_num, choice.label)
                raise ParserError(msg)
            choice.next_snippet = snippets[tgt_ref_num][0]

    # Attempt to detect orphaned snippets
    root_snip = snippets[min(snippets.keys())][0]
    reachable_snippets = root_snip.get_snippets_tree()
    if len(snippets) != len(reachable_snippets):
        msg = ('Number of total snippets (count: {}) not equal to number '
               'of snippets reachable from the snippet with lowest '
               'reference number (count: {})'
              ).format(len(snippets), len(reachable_snippets))
        raise ParserError(msg)

    return snippets, directives


def get_directives(textlines):
    """Finds directives and also prunes them from input textlines"""
    skiplines = 0
    given_directives = dict()

    # Parse textlines for directives
    for line in textlines:
        d = re.search(DIRECTIVE_IDENT_STR + r'(.*)', line)
        if not d:
            # All directives are at the top of the document. Halt when no more
            # directives are encountered.
            break

        directive = d.groups()[0]
        arg = None
        if DIRECTIVE_ARG_SEPARATOR in directive:
            directive, arg = directive.split(DIRECTIVE_ARG_SEPARATOR, 1)

        if directive not in DIRECTIVES:
            msg = '"{}" is not a valid directive'.format(directive)
            raise ParserError(msg)

        skiplines += 1

        expected_type = DIRECTIVES[directive]
        if expected_type is None:
            # If directive takes no args, treat it as a switch then move on to
            # the next directive
            given_directives[directive] = True
            continue
        
        # If directive takes args, do typechecking
        if arg is None:
            msg = ('The directive "{}" requires an argument but none was '
                   'provided (syntax: "{}{}{}argument" without the '
                   'surrounding doublequotes)'
                  ).format(DIRECTIVE_IDENT_STR, directive,
                           DIRECTIVE_ARG_SEPARATOR)
            raise ParserError(msg)
        
        # Cast the given argument (which is a str) to the expected_type
        try:
            given_directives[directive] = expected_type(arg)
        except:
            msg = ('bad argument type to directive {} (expected {}, got {})'
                  ).format(directive, expected_type, str(arg))
            raise ParserError(msg)

    # 
    if not given_directives.get('ROOT_SNIP_ID', None):
        msg = ('You must declare the "ROOT_SNIP_ID" directive. This will be '
               'the snip_id assigned to your root snippet.')
        raise ParserError(msg)

    # Handle directives dependencies/implications
    if given_directives.get('OVERWRITE_DB_SNIP_IDS', None):
        if not given_directives.get('REF_NUMS_ARE_SNIP_IDS', None):
            msg = ('The "OVERWRITE_DB_SNIP_IDS" directive requires the '
                   '"REF_NUMS_ARE_SNIP_IDS" to be declared as well.')
            raise ParserError(msg)

    # Return directives and the textlines with directive lines pruned out
    return textlines[skiplines:], given_directives


def complain(thing, line_num, problem):
    msg = '{thing} at line {line_num} has {problem}'.format(**locals())
    raise ParserError(msg)


def interpret(textlines, comment_marker=None):
    """Generates ref_num, game_text, list(Choices) from input list(str)"""
    last_ref_num = None
    game_text = None
    choice_whitespace = ''
    choices = []

    # We're appending <<EOF>> to the end of the loop as a sentinel value
    for i, line in enumerate(textlines + ['<<EOF>>']):
        # Flag for the last loop
        last_line = line is '<<EOF>>'

        # Trim off comments
        if (comment_marker is not None and
            not last_line
        ):
            line = trim_comment(line, comment_marker)

        # Ignore line if it's empty
        if (line.strip() is '' and 
            i+1 < len(textlines)
        ):
            continue

        if not starts_new_snippet(line):
            # If we have seen a choice and the whitespace here doesn't look
            # like the whitespace used for the choice, treat as a flag
            # operation definition
            if choice_whitespace and get_indent(line) != choice_whitespace:
                latest_choice = choices[-1]
                method, expr = parse_flag(i+1, line)
                try:
                    if method is 'check':
                        latest_choice.add_check_flag(expr)
                    else:
                        latest_choice.add_modifies_flag(expr)
                except BadExpressionError:
                    complain('Choice flag operation', i+1, 'bad expression')
                continue
        
            # Otherwise since the whitespace is the same as used by the last
            # choice we saw, treat this as a choice definition
            # Update the whitespace definition if it's not defined yet
            if not choice_whitespace:
                choice_whitespace = re.search(r'^(\s+)', line).groups()[0]
            
            label, ref_num = parse_choice(i+1, line)
            choices.append(Choice(label, int(ref_num or last_ref_num + 1)))
            continue

        # Since starts_new_snippet(line):
        # If not first line, not last line, but we don't see any Choices
        # defined, complain:
        if ((not choices) and
            (i > 0) and 
            (not last_line)
        ):
            complain('Last snippet before new snippet/end of text', i+1, 
                     'no choices defined')

        # Otherwise we can flush last_ref_num, game_text and choices as 
        # outputs representing a single snippet:
        # Store previous loop vars in output vars
        pv_ref_num, pv_game_text, pv_choices = last_ref_num, game_text, choices
        
        # Update/reset the loop vars for new snippet
        if not last_line:
            last_ref_num, game_text = parse_game_text(i+1, line)
            choices, choice_whitespace = [], ''

        if i == 0:
            continue
        # Yield the stored output vars
        yield pv_ref_num, pv_game_text, pv_choices


def parse_choice(line_idx, line):
    line = line.strip()
    label = next_ref_num = None
    ref_num_str = None

    label, *ref_num_str = line.split('->', 1)
    if not label:
        complain('Choice', line_idx, 'no label defined')

    if ref_num_str:
        s = re.search(r'(\d+)', ref_num_str[0])
        if not s:
            complain('Choice', line_idx, 'no reference number found')
        next_ref_num = int(s.groups()[0])

    label = label.strip()
    
    print('------>   Choice:', label, next_ref_num)
    return label, next_ref_num


def parse_flag(line_idx, line):
    line = line.strip()
    check_or_modifies = output_expr = None

    if line.startswith('Req'):
        words = line.split(None, 1)
        if len(words) < 2:
            complain('Flag expression', line_idx, 'missing expression')
        check_or_modifies = 'check'
        output_expr = words[1]

    else:
        check_or_modifies = 'modifies'
        output_expr = line

    print('------>     flag:', check_or_modifies, output_expr)
    return check_or_modifies, output_expr


def parse_game_text(line_idx, line):
    output = None
    s = re.search(r'^\D*(\d+)\S*\s+(.*)', line)
    if not s:
        complain('Snippet', line_idx, 'does not have a reference number')
    ref_num, game_text = s.groups()
    print('------> gametext:', ref_num, game_text[:20]+'...')
    return int(ref_num), game_text.strip()


def get_ref_num(line):
    output = None
    s = re.search(r'^\S*(\d+)', line)
    if s:
        output = s.groups()[0]
    return output


def starts_new_snippet(line):
    # if start of string has no whitespace, this is a new snippet
    return re.search(r'^\s+', line) is None


def get_indent(line):
    return re.search(r'^(\s+)', line).groups()[0]


def trim_comment(line, comment_marker):
    if comment_marker in line:
        line = line.split(comment_marker, 1)[0]
    return line
