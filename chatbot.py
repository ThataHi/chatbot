import sqlite3
import re

def interpretar_mensagem(mensagem):
    curso_match = re.search(r"(ads|engenharia)", mensagem.lower())
    dia_match = re.search(r"(segunda|terça|quarta|quinta|sexta)", mensagem.lower())

    if not curso_match or not dia_match:
        return "Por favor, informe o curso e o dia da semana."

    curso = curso_match.group(1)
    dia = dia_match.group(1)

    return buscar_horario(curso, dia)

def buscar_horario(curso, dia):
    conn = sqlite3.connect('horarios.db')
    c = conn.cursor()

    c.execute("SELECT horario, disciplina FROM horarios WHERE curso=? AND dia=?", (curso, dia))
    resultado = c.fetchone()
    conn.close()

    if resultado:
        horario, disciplina = resultado
        return f"{curso.upper()} na {dia.capitalize()}: {horario} - {disciplina}"
    else:
        return f"Não encontrei aula para {curso.upper()} na {dia.capitalize()}."
