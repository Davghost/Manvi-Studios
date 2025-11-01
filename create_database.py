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

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
   id INTEGER PRIMARY KEY,
   username TEXT NOT NULL UNIQUE,
   email TEXT NOT NULL UNIQUE,
   password_hash TEXT NOT NULL,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   last_login DATETIME
   );
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS user_answer(
   id INTEGER PRIMARY KEY,
   user_id INTEGER NOT NULL,
   exam_id INTEGER NOT NULL,
   question_id INTEGER NOT NULL,
   selected_option TEXT NOT NULL CHECK(selected_option IN ('A', 'B', 'C', 'D')),
   answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (user_id) REFERENCES users (id),
   FOREIGN KEY (exam_id) REFERENCES exam (id),
   FOREIGN KEY (question_id) REFERENCES question(id)
   );
""")

cur.execute("""
   CREATE TABLE IF NOT EXISTS user_profile(
   id INTEGER PRIMARY KEY,
   user_id INTEGER NOT NULL UNIQUE,
   name TEXT NOT NULL,
   profile_picture TEXT,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   institution TEXT NOT NULL,
   birth_date DATE NOT NULL,
   bio TEXT,
   country TEXT,
   city TEXT,
   state TEXT,
   FOREIGN KEY (user_id) REFERENCES users(id)
   )
""")

con.commit()
cur.close()
con.close()