
CREATE TABLE WORDS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL,
    word TEXT NOT NULL,
    word_letter_cased TEXT NOT NULL,
    date_first_used TEXT NOT NULL,
    part_of_speech TEXT NOT NULL,
    word_break TEXT NOT NULL,
    pronounce TEXT NOT NULL,
    audio TEXT NOT NULL,
    etymology TEXT NOT NULL,
    definitions TEXT NOT NULL,
    example TEXT NOT NULL
);