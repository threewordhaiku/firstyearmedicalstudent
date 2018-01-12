class ChoiceError(Exception):
    """Basic exception for errors raised by Choices"""
    def __init__(self, choice, msg=None):
        if msg is None:
            msg = "An error occured with choice %s" % str(choice)
        super(ChoiceError, self).__init__(msg)
        self.choice = choice


class BadExpression(ChoiceError):
    """Bad expression provided to Choice"""
    def __init__(self, choice, expr, msg=None):
        if msg is None:
            msg = ('Bad expression provided for choice {} '
                   '(expected "flag_name->str operator->str value->int", '
                   'got "{}")'
                ).format(choice, expr)
        super(BadExpression, self).__init__(choice, msg=msg)
        self.choice = choice
        self.expression = expr




class SnippetError(Exception):
    """Basic exception for errors raised by Snippets"""
    def __init__(self, snippet, msg=None):
        if msg is None:
            msg = ("An error occured with snippet {}"
                  ).format(str(snippet))
        super(SnippetError, self).__init__(msg)
        self.snippet = snippet


class CannotRedefineSnipID(SnippetError):
    """Attempted to redefine snip_id in committed snippet"""
    def __init__(self, snippet):
        msg = ('Attempted to overwrite snip_id {} for snippet {} '
               '(has this snippet already been committed?)'
              ).format(snippet.snip_id, str(snippet))
        super(CannotRedefineSnipID, self).__init__(snippet, msg=msg)
        self.snip_id = snippet.snip_id
        self.snippet = snippet


class ConflictingSnipID(SnippetError):
    """Attempted to redefine snip_id in uncommitted snippet"""
    def __init__(self, snippet, incoming_snip_id):
        msg = ('Attempted to overwrite snip_id {} for snippet {} '
               '(conflict resolution strategy not provided while generating '
               'snip_ids for committing to db)'
              ).format(snippet.snip_id, str(snippet))
        super(CannotRedefineSnipID, self).__init__(snippet, msg=msg)
        self.snip_id = snippet.snip_id
        self.incoming_snip_id = incoming_snip_id
        self.snippet = snippet


class TerminalSnippetError(SnippetError):
    """Attempted to modify a Terminal Snippet unacceptably"""
    def __init__(self, snippet, msg=None, hint=''):
        if msg is None:
            msg = ('Attempted invalid action on Terminal Snippet {}'
                  ).format(str(snippet), hint)
        super(TerminalSnippetError, self).__init__(snippet, msg=msg)
        self.snippet = snippet



class CompilerError(Exception):
    """Basic exception for errors raised by Snippets"""
    def __init__(self, hint=None):
        if hint is None:
            hint = ("An error occured while compiling snippets into the "
                    "database. No changes were committed.")
        super(CompilerError, self).__init__(hint)


class TimidError(CompilerError):
    """Basic exception for errors raised by Snippets"""
    def __init__(self, snip_id, hint=None):
        if hint is None:
            hint = ('snip_id {} already exists in the database, "timid" '
                    'insert method aborted'.format(
                        snip_id
                   ))
        super(TimidError, self).__init__(hint)


