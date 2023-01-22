CREATE USER akcay;
CREATE DATABASE ai_db;
GRANT ALL PRIVILEGES ON DATABASE ai_db TO akcay;

\c ai_db;

CREATE TABLE transactions (
  transaction_date DATE
);

INSERT INTO transactions VALUES ('2022-01-01');
INSERT INTO transactions VALUES ('2022-03-02');
INSERT INTO transactions VALUES ('2022-05-03');
INSERT INTO transactions VALUES ('2022-07-04');
INSERT INTO transactions VALUES ('2022-09-05');
INSERT INTO transactions VALUES ('2022-11-06');
INSERT INTO transactions VALUES ('2023-01-07');
INSERT INTO transactions VALUES ('2023-03-08');
INSERT INTO transactions VALUES ('2023-05-09');
INSERT INTO transactions VALUES ('2023-07-10');