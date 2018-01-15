INSERT INTO 
    saved_games(my_name, my_fruit, flag1, flag2, flag3)
VALUES
    ('Sir Arthur, King of the Britains', 'guava', 1, 2, 3),
    ('Patsy, Arthur''s Servant', 'coconut', null, 5, 6),
    ('Sir Lancelot the Brave', 'watermelon', 7, null, 8),
    ('Sir Robin the Not-Quite-So-Brave-as-Sir-Lancelot', 'bat guano', null, null, null),
    ('Sir Bedevere the Wise', 'duckfruit', 1, null, null);



INSERT INTO
    snippets(snip_id, game_text)
VALUES
    (1, 'I looked at the tablet Dr. Hanson had given to me. It contained a list of patients I was tasked with checking on.'),
    (2, '“John Doe. Ward 1A. Admitted on {date} {time}. Severe diarrhea and vomiting. Follow up required”  The details of my first patient was displayed on the screen next to a picture of a plump young man.'),
    (3, 'I walked up to the first bed in the ward and drew the curtains. I almost thought I had the wrong person until I noticed the nameplate behind the bedrest. The illness has certainly taken a toll on John.'),
    (4, 'John stares at you, his eyes seemingly lifeless.'),
    (5, '"Not too good, doctor. Not too good."'),
    (6, '"What?"'),
    (7, '"..."');



INSERT INTO
    choices(
        choice_label, snip_id, next_snip_id,
        mod_flg_1, mod_flg_2, mod_flg_3, 
        check_flg_1, check_flg_2, check_flg_3
    )
VALUES
    (
        'How are you feeling?', 4, 5,
        null, null, null,
        null, null, null
    ), (
        'You look great today.', 4, 6,
        'bm_patient += 1', null, null,
        null, null, null
    ), (
        'You look wonderful!', 6, 7,
        'bm_patient += 1', null, null,
        null, null, null
    ), (
        'How are you feeling?', 6, 5,
        null, null, null,
        null, null, null
    );