DROP TABLE IF EXISTS saved_games;
CREATE TABLE "saved_games" (
    game_id serial PRIMARY KEY,
    my_name text NOT NULL,
    my_fruit text NOT NULL,
    flag1 int,
    flag2 int,
    flag3 int
);

DROP TABLE IF EXISTS snippets;
CREATE TABLE "snippets" (
    snip_id serial PRIMARY KEY,
    game_text text not null
);

DROP TABLE IF EXISTS choices;
CREATE TABLE "choices" (
    choice_id serial PRIMARY KEY,
    choice_label text not null,
    snip_id int not null,
    next_snip_id int not null,
    
    set_flg_1 text,
    set_val_1 int,
    set_flg_2 text,
    set_val_2 int,

    check_flg_1 text,
    check_opr_1 text,
    check_val_1 int,
    check_flg_2 text,
    check_opr_2 text,
    check_val_2 int,

    FOREIGN KEY (snip_id) REFERENCE snippets(snip_id),
    FOREIGN KEY (next_snip_id) REFERENCE snippets(snip_id)
);