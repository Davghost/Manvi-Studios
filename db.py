import sqlite3

DB_PATH = "questions_bank.db"

def get_connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con