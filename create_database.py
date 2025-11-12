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
   submission_exam_id INTEGER,
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
   serie TEXT,
   FOREIGN KEY (user_id) REFERENCES users(id)
   )
""")

cur.execute("""
   CREATE TABLE IF NOT EXISTS teachers(
   id INTEGER PRIMARY KEY,
   username TEXT NOT NULL UNIQUE,
   email TEXT NOT NULL UNIQUE,
   password_hash TEXT NOT NULL,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   last_login DATETIME
   );
""")

cur.execute("""
   CREATE TABLE IF NOT EXISTS teacher_profile(
   id INTEGER PRIMARY KEY,
   teacher_id INTEGER NOT NULL UNIQUE,
   name TEXT NOT NULL,
   profile_picture TEXT,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   institution TEXT NOT NULL,
   birth_date DATE NOT NULL,
   bio TEXT,
   country TEXT,
   city TEXT,
   state TEXT,
   FOREIGN KEY (teacher_id) REFERENCES teachers(id)
   )
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS escolas (
    codigo_inep TEXT PRIMARY KEY,
    nome TEXT,
    municipio TEXT,
    uf TEXT,
    regiao TEXT,
    ano_censo TEXT,
    cep TEXT,
    nome_uf TEXT
);
""")

con.commit()
cur.close()
con.close()