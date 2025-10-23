#importa de método fixo(não dinâmico) as questões das provas paulistas
#prova_1bim9ano/dia1.txt
import sqlite3
import os

con = sqlite3.connect("questions_bank.db")

cur = con.cursor()

exam_title = "Prova Paulista 2025 - 1º Bim 9º Ano"

exam_description = "Prova paulista 2025 - primeiro bimestre - nível 9° ano"

cur.execute(
    "INSERT INTO exam (title, description) VALUES (?, ?)",
    (exam_title, exam_description)
)

exam_id = cur.lastrowid

file_path = "data/exams/provas_paulista2025/prova_1bim9ano/dia1.txt"

with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()

raw_questions = content.strip().split("\n\n")

for question_text in raw_questions:
    
    lines = question_text.strip().split("\n")
    
    opt_indices = []
    
    for i, line in enumerate(lines):
        if line.startswith("A)") or line.startswith("B)") or line.startswith("C)") or line.startswith("D)"):
            opt_indices.append(i)
    
    
    statement_lines = lines[:opt_indices[0]]
    statement = " ".join(statement_lines).strip()

    opt_a = lines[opt_indices[0]][2:].strip()
    opt_b = lines[opt_indices[1]][2:].strip()
    opt_c = lines[opt_indices[2]][2:].strip()
    opt_d = lines[opt_indices[3]][2:].strip()
    
    correct_option = None
    for line in lines:
        if line.lower().startswith("resposta:"):
            correct_option = line.split(":")[1].strip().upper()
            break

    cur.execute(
        """
        INSERT INTO question
        (exam_id, statement, opt_a, opt_b, opt_c, opt_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (exam_id, statement, opt_a, opt_b, opt_c, opt_d, correct_option)
    )

con.commit()
cur.close()
con.close()

print("Importação concluída com sucesso!")
