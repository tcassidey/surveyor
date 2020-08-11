-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS experiment_data;

DROP TABLE IF EXISTS user; 
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  treatment_level INTEGER,
  slide_number INTEGER,
  simulation_period INTEGER,
  current_stage TEXT,
  gender TEXT,
  age INTEGER,
  sc_exp INTEGER,
  procurement_exp INTEGER,
  CRT1 INTEGER, CRT2 INTEGER, CRT3 INTEGER, CRT4 INTEGER, CRT5 INTEGER, 
  CRT6 INTEGER, CRT7 INTEGER,
  Fin1 INTEGER, Fin2 INTEGER, Fin3 INTEGER, Fin4 INTEGER, Fin5 INTEGER,
  Fin6 INTEGER,
  RP1 INTEGER, RP2 INTEGER, RP3 INTEGER, RP4 INTEGER, RP5 INTEGER, RP6 INTEGER,
  RP7 INTEGER, RP8 INTEGER, RP9 INTEGER,
  RP10 INTEGER, feedback TEXT, enter_simulation TEXT,
  calculator_count INTEGER,
  CONSTRAINT unique_login UNIQUE (username)
);

DROP TABLE IF EXISTS contracts;
CREATE TABLE contracts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  simulation_period INTEGER NOT NULL,
  q INTEGER NOT NULL,
  calculator_count INTEGER,
  time_stamp TEXT
)

