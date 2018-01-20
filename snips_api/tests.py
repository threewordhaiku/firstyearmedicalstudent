"""
unittests for the snips_api module


Usage:

    # firstyearmedicalstudent/runtests.py
    import unittest
    import snips_api.tests
    unittest.main(snips_api.tests)

    $ python firstyearmedicalstudent/runtests.py
"""


import unittest
import os

from . import snips_parser
from .components import *

SAMPLE_TEXT = """
directive:COMMENT_MARKER //
directive:ROOT_SNIP_ID 123
28. Introducing myself, I took a chair and sat beside John.
    How are you feeling?  -> (29)
    You’re looking good today. -> (30)
        bm_patient += 1


// This is a comment
  // Another comment
29. John: “Ah, doctor. Not too good…”
    Next -> (31)                          // Yet another comment
30. John: “What?”
    Next
31. This is going to be a long day...
"""



def _setup_dburl():
    if 'DATABASE_URL' not in os.environ:
        os.environ['DATABASE_URL'] = """postgres://bsthemqyqomnye:62b3461d8590acc3ff6d1da2dbdea6149f8dbd4e84c4e4495e5558ae0debecde@ec2-54-227-250-33.compute-1.amazonaws.com:5432/d610ss6vui1oit"""


class ComponentsTestCase(unittest.TestCase):
    def test_api(self):
        s_start = RootSnippet(9000, 'Dr. Smith: "Okay, last question. If a runaway train is bearing down--"')
        s_nointerrupt = Snippet('Dr. Smith: "--well, actually, I think you know the rest of it. What do you think?"')
        s_nointerrupt2 = Snippet('Dr. Smith: "Hmm, I see. Alright, that\'s all for today. Thanks for coming down."')
        s_interrupted = Snippet('Dr. Smith: "Oh. I see. Well then, I think that\'s all for today."')
        end = TerminalSnippet('That was a strange interview...')

        s_start.add_choice(
            "(You've heard this one before...)",
            next_snippet=s_nointerrupt)

        s_nointerrupt.add_choice(
            "I won't do anything",
            next_snippet=s_nointerrupt2
                ).add_modifies_flag('tut_switch_track = 0')
        s_nointerrupt.add_choice(
            "I'd switch the tracks",
            next_snippet=s_nointerrupt2
                ).add_modifies_flag('tut_switch_track = 1')

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

        expected_result = [s_start, s_nointerrupt, s_interrupted, 
                           s_nointerrupt2, end]
        self.assertEqual(s_start.get_snippets_tree(), expected_result, 
                         'failed on s_start.get_snippets_tree()')


class ParsingTestCase(unittest.TestCase):
    def setUp(self):
        _setup_dburl()

    def test_parse(self):
        parse_output = [
            ('INSERT INTO snippets(snip_id, game_text) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s)', 
                [
                    'John: “Ah, doctor. Not too good…”', 124, 
                    'John: “What?”', 125, 
                    'This is going to be a long day...', 126, 
                    'Introducing myself, I took a chair and sat beside John.', 123
                ]
            ), ('INSERT INTO choices(choice_label, snip_id, next_snip_id, mod_flg_1, mod_flg_2, mod_flg_3, check_flg_1, check_flg_2, check_flg_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', ['How are you feeling?  ', 123, 124, None, None, None, None, None, None]), ('INSERT INTO choices(choice_label, snip_id, next_snip_id, mod_flg_1, mod_flg_2, mod_flg_3, check_flg_1, check_flg_2, check_flg_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', ['You’re looking good today. ', 123, 125, 'bm_patient += 1', None, None, None, None, None]), ('INSERT INTO choices(choice_label, snip_id, next_snip_id, mod_flg_1, mod_flg_2, mod_flg_3, check_flg_1, check_flg_2, check_flg_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', ['Next ', 124, 126, None, None, None, None, None, None]), ('INSERT INTO choices(choice_label, snip_id, next_snip_id, mod_flg_1, mod_flg_2, mod_flg_3, check_flg_1, check_flg_2, check_flg_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                [
                    'Next', 125, 126, None, None, None, None, None, None
                ]
            )
        ]
        output = [x for x in snips_parser.parse(SAMPLE_TEXT)]
        self.assertEqual(output, parse_output, 'bad parser output')





