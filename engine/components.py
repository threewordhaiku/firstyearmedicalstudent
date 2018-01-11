from collections import OrderedDict

from .exceptions import *
from .compiler import snippet_chain_to_sql_data


class Choice():
    def __init__(self, label, next_snippet):
        self.label = label
        self.next_snippet = next_snippet

        self.check_flags = []
        self.modifies_flags = []

    @property
    def snippet(self):
        return self._fromsnip
    

    def add_check_flag(self, expression):
        flag_name, operator, value = self.parse_expression(expression)
        self.check_flags.append(
            (flag_name, operator, value)
        )


    def add_modifies_flag(self, expression):
        flag_name, operator, value = self.parse_expression(expression, 
            use_symbols='assignment')
        self.modifies_flags.append(
            (flag_name, operator, value)
        )


    def parse_expression(self, expr, use_symbols='comparison'):
        try:
            # Unpack
            flag_name, operator, value = str(expr).split()
            
            # Cast types
            flag_name = str(flag_name)
            operator = str(operator)
            value = int(value)

            # Ensure valid
            self.ensure_valid_flag_name(flag_name)
            self.ensure_valid_operator(operator, use_symbols)
        
        # Re-raise BadExpressions from ensure_valid funcs, if any
        except BadExpression:
            raise
        # Otherwise raise generic BadExpression
        except:
            #raise BadExpression(self, str(expr))
            raise
        return flag_name, operator, value


    def ensure_valid_flag_name(self, flag_name): 
        accept_chars = "_abcdefghijklmnopqrstuvwxyz"
        accept_chars += accept_chars.upper()
        for c in flag_name:
            if c not in accept_chars:
                msg = 'invalid flagname "{}" (use letters and underscore)'
                raise BadExpression(self, flag_name, msg.format(flag_name))


    def ensure_valid_operator(self, oper, symbol_set):
        operators = dict(
            comparison=(
                '== != '        # equivalence
                '< > <= >= '    # magnitude
            ).split(),
            
            assignment=(
                '= += -= *= /= '  # assignment
            ).split()
        )
        if symbol_set not in operators:
            raise Exception('Invalid operator set selection '
                            '(expecting "comparison" or "assignment")')
        accept_opers = operators[symbol_set]

        if oper not in accept_opers:
            msg = 'invalid operator "{}" (use {})'.format(
                oper, ', '.join(accept_opers))
            raise BadExpression(self, oper, msg)


    def make_sql(self):
        pass


    def __repr__(self):
        """Pretty-print Choice object"""
        fr = self.snippet.snip_id
        to = self.next_snippet
        label = self.label
        if len(label) > 20:
            label = label[:17] + '...'
        m = '<Choice {fr}~{to}: {label}>'
        return m.format(**locals())



class Snippet():
    def __init__(self, text, **kwargs): 
        self.text = text
        self.choices = []
        self.snip_id = 'pending'
        self.committed = False

        self.metadata = dict()
        # Copy metadata vars
        for key in ['author', 'description']:
            if key not in kwargs:
                continue
            self.metadata[key] = kwargs[key]
    
    
    def ensure_has_snip_id(self):
        """Decorator for enforcing methods that require snip_id"""
        if self.snip_id == 'pending':
            raise SnippetError("Cannot proceed because Snippet does not "
                               "have a snid_id")


    def set_text(self, text):
        self.text = text


    def set_snip_id(self, snip_id):
        if self.snip_id is not 'pending':
            raise CannotRedefineSnipID(self)
        self.snip_id = snip_id


    def get_assigned_snip_id(self):
        return self.snip_id


    def add_choice(self, *args, **kwargs):
        c = Choice(*args, **kwargs)
        c._fromsnip = self  # Special attr used for convenience
        self.choices.append(c)
        return c


    def get_child_snippets(self):
        """Gets all 'downstream' Snippets connected to this one"""
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
        snip_id = int(use_snip_id) or self.snip_id
        game_text = self.text
        # http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries
        sql = """INSERT INTO snippets(snip_id, game_text) VALUES (%s %s)"""
        data = (snip_id, game_text)
        return sql, data


    def generate_chain_sql(self):
        query, data = snippet_chain_to_sql_data(self)
        return query, data


    def __repr__(self):
        """Pretty-print Snippet object"""
        snip_id = self.snip_id
        text = self.text
        if len(text) > 20:
            text = text[:17] + '...'
        m = '<Snippet id-{snip_id}: {text}>'
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
        m = '<TerminalSnippet id-{snip_id}: {text}>'
        return m.format(**locals())



class RootSnippet(Snippet):
    """Special Snippet class denoting start of a chain of Snippets"""
    def __init__(self, *args, **kwargs):
        super(RootSnippet, self).__init__(*args, **kwargs)


    def compile(self):
        self.ensure_has_snip_id()
        compile_snippet(self)


    def __repr__(self):
        """Pretty-print Snippet object"""
        snip_id = self.snip_id
        text = self.text
        if len(text) > 20:
            text = text[:17] + '...'
        m = '<RootSnippet id-{snip_id}: {text}>'
        return m.format(**locals())

