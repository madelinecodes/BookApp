CREATE TABLE users (
    username VARCHAR(255),
    password VARCHAR(255)
);

CREATE TABLE books (
    ISBN VARCHAR NOT NULL,
    Title VARCHAR NOT NULL,
    Author VARCHAR NOT NULL,
    PubYear VARCHAR NOT NULL
);


CREATE TABLE reviews (
    users VARCHAR NOT NULL,
    review VARCHAR,
    rating VARCHAR,
    isbn VARCHAR
);


CREATE TABLE reviews (
    users VARCHAR NOT NULL,
    review VARCHAR,
    rating VARCHAR,
    isbn VARCHAR
);