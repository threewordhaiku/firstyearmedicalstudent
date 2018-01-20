from collections import OrderedDict
from .exceptions import *

VALID_OPERATORS_COMPARISON = '== != <= >= < >'
VALID_OPERATORS_ASSIGNMENT = '= += -= *= /='


class Choice():
    def __init__(self, label, next_snippet):
        self.label = label
        self.next_snippet = next_snippet
        self.from_snip = None

        self.check_flags = []
        self.modifies_flags = []

    @property
    def snippet(self):
        return self.from_snip
    

    def set_source_snip(self, snip):
        self.from_snip = snip


    def add_check_flag(self, expression):
        expr = self.parse_expression(expression)
        self.check_flags.append(expr)
        return self


    def add_modifies_flag(self, expression):
        expr = self.parse_expression(expression, 
            use_symbols='assignment')
        self.modifies_flags.append(expr)
        return self


    def parse_expression(self, expr, use_symbols='comparison'):
        try:
            # Unpack
            flag_name, operator, value = str(expr).split()
            
            # Typechecking; this triggers ValueErrors
            flag_name = str(flag_name)
            operator = str(operator)
            value = int(value)

            # Ensure valid
            self.ensure_valid_flag_name(flag_name)
            self.ensure_valid_operator(operator, use_symbols)
        
        # Re-raise BadExpressionErrors from ensure_valid funcs, if any
        except BadExpressionError:
            raise
        # Otherwise raise generic BadExpressionError
        except:
            raise BadExpressionError(self, str(expr))
        return '{flag_name} {operator} {value}'.format(**locals())


    def ensure_valid_flag_name(self, flag_name): 
        accept_chars = "_abcdefghijklmnopqrstuvwxyz"
        accept_chars += accept_chars.upper()
        for c in flag_name:
            if c not in accept_chars:
                msg = 'invalid flagname "{}" (use letters and underscore)'
                raise BadExpressionError(self, 
                                         flag_name,
                                         msg.format(flag_name))


    def ensure_valid_operator(self, oper, symbol_set):
        operators = dict(
            comparison=VALID_OPERATORS_COMPARISON.split(),
            assignment=VALID_OPERATORS_ASSIGNMENT.split()
        )
        if symbol_set not in operators:
            raise Exception('Invalid operator set selection '
                            '(expecting "comparison" or "assignment")')
        accept_opers = operators[symbol_set]

        if oper not in accept_opers:
            msg = 'invalid operator "{}" (use {})'.format(
                oper, ', '.join(accept_opers))
            raise BadExpressionError(self, oper, msg)


    def __repr__(self):
        """Pretty-print Choice object"""    
        label = self.label
        if len(label) > 25:
            label = label[:22] + '...'
        
        fr = to = ''
        if self.snippet:
            fr = ' from ' + str(self.snippet.snip_id)
        if fr and self.next_snippet:
            to = ' to ' + str(self.next_snippet.snip_id)
        
        m = '<Choice{fr}{to}: {label}>'
        return m.format(**locals())



class Snippet():
    def __init__(self, text, snip_id=None): 
        self.text = text
        self.choices = []
        self.snip_id = snip_id or 'pending'


    def set_snip_id(self, snip_id):
        if self.snip_id is not 'pending':
            raise CannotRedefineSnipIDError(self)
        self.snip_id = snip_id


    def add_choice(self, *args, **kwargs):
        c = Choice(*args, **kwargs)
        c.set_source_snip(self)  # Special attr used for convenience
        self.choices.append(c)
        return c


    def get_snippets_tree(self):
        """Gets all reachable snippets, including this one"""
        if getattr(self, 'child_snippets', None):
            return self.child_snippets
        unwalked = [self]
        seen = OrderedDict()

        while unwalked:
            snip = unwalked.pop(0)
            seen[snip] = True
            for c in snip.choices:
                if c.next_snippet not in seen:
                    unwalked.append(c.next_snippet)

        self.child_snippets = [x for x in seen.keys()]
        return self.child_snippets


    def make_insert_args(self, use_snip_id=None):
        snip_id = use_snip_id or self.snip_id
        try:
            int(snip_id)
        except ValueError:
            SnippetError('Bad argument for snip_id '
                         '(expecting type int, got {}'.format(repr(snip_id))
                        )
        game_text = self.text
        # http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries
        sql = """INSERT INTO snippets(snip_id, game_text) VALUES (%s %s)"""
        data = (snip_id, game_text)
        return sql, data


    def generate_chain_sql(self, insert_method='timid'):
        from .compiler import snippet_chain_to_sql_data
        for query, data in snippet_chain_to_sql_data(self, insert_method):
            yield query, data


    def __repr__(self):
        """Pretty-print Snippet object"""
        snip_id = self.snip_id
        text = self.text
        if len(text) > 25:
            text = text[:22] + '...'
        m = '<Snippet id {snip_id}: {text}>'
        return m.format(**locals())



class TerminalSnippet(Snippet):
    """Special Snippet class denoting end of a chain of Snippets"""
    def __init__(self, *args, **kwargs):
        super(TerminalSnippet, self).__init__(*args, **kwargs)


    def add_choice(self, *args, **kwargs):
        """Block attempts to extend choices"""
        msg = 'Cannot extend choices from Terminal Snippet {}'.format(self)
        raise TerminalSnippetError(self, msg)
        return


    def __repr__(self):
        """Pretty-print Snippet object"""
        snip_id = self.snip_id
        text = self.text
        if len(text) > 20:
            text = text[:17] + '...'
        m = '<TerminalSnippet id {snip_id}: {text}>'
        return m.format(**locals())



class RootSnippet(Snippet):
    """Special Snippet class denoting start of a chain of Snippets"""
    def __init__(self, snip_id, text, *args, **kwargs):
        try:
            super(RootSnippet, self).__init__(
                text, int(snip_id), *args, **kwargs)
        except ValueError:
            msg = 'Bad snip_id provided (expected int, got: {})'.format(
                repr(snip_id))
            raise SnippetError(self, msg=msg)


    def __repr__(self):
        """Pretty-print Snippet object"""
        snip_id = self.snip_id
        text = self.text
        if len(text) > 20:
            text = text[:17] + '...'
        m = '<RootSnippet id {snip_id}: {text}>'
        return m.format(**locals())
