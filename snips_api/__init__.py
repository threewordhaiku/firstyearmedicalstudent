from .components import *  # Make components available with
                           # "from snips_api import Snippet, Choice"

def lookup_snippet(snip_id):
    raise NotImplementedError


def pprint_generator(gen, maxcols=60):
    """Pretty-prints the generator output from Snippet.generate_chain_sql()

    Usage:
        gen = my_snippet.generate_chain_sql()
        pprint_generator(gen)
    """
    def trunc(t):
        if len(t) > maxcols:
            t = t[:maxcols - 3] + '...'
        return t

    for sql, data in gen: 
        print(trunc(sql))
        if 'INSERT INTO snippets' in sql:
            d = list(data)
            for i in range(len(d)// 2):
                print('   ', d[i * 2 + 1], trunc(d[i * 2]))
        else:
            print('   ', data)

