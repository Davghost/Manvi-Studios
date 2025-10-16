import sqlite3

con = sqlite3.connect("questions_bank.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS exam(
   id INTEGER PRIMARY KEY,
   title TEXT NOT NULL,
   description TEXT,
   created DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS question(
   id INTEGER PRIMARY KEY,
   exam_id INTEGER NOT NULL,
	statement TEXT NOT NULL,
   opt_a TEXT NOT NULL,
   opt_b TEXT NOT NULL,
   opt_c TEXT NOT NULL,
   opt_d TEXT NOT NULL,
   correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
   FOREIGN KEY (exam_id) REFERENCES exam (id)
   );
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS user_result(
   id INTEGER PRIMARY KEY,
   exam_id INTEGER NOT NULL,
   correct INTEGER NOT NULL,
   total INTEGER NOT NULL,
   date DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (exam_id) REFERENCES exam (id)
   );
""")

con.commit()
cur.close()
con.close()