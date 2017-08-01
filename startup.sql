CREATE TABLE COMPANY (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    short_description TEXT NOT NULL,
    perma TEXT NOT NULL UNIQUE,
    created date NOT NULL
);