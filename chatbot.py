import sqlite3
import re

def interpretar_mensagem(mensagem):
    mensagem = mensagem.lower()

    # Saudações
    if re.search(r"\b(oi|olá|bom dia|boa tarde|boa noite)\b", mensagem):
        return "Olá! Como posso te ajudar hoje?"

    # Agradecimentos
    if re.search(r"\b(obrigado|valeu|agradecido)\b", mensagem):
        return "De nada! Qualquer coisa, estou por aqui. 😊"

    # Educação
    if re.search(r"\b(por favor|poderia|poderia me informar|seria possível)\b", mensagem):
        return "Claro! Pode me dizer o curso e o dia da semana?"

    # Solicitação de horário
    curso_match = re.search(r"\b(ads|engenharia)\b", mensagem)
    dia_match = re.search(r"\b(segunda|terça|quarta|quinta|sexta)\b", mensagem)

    if curso_match and dia_match:
        curso = curso_match.group(1)
        dia = dia_match.group(1)
        return buscar_horario(curso, dia)

    # Se mencionou só curso
    if curso_match and not dia_match:
        return "Você mencionou o curso, mas não disse o dia. Qual dia da semana você quer saber?"

    # Se mencionou só dia
    if dia_match and not curso_match:
        return "Você mencionou o dia, mas não disse o curso. Qual curso você quer saber?"

    # Mensagem genérica não compreendida
    return "Desculpe, não entendi. Você pode perguntar, por exemplo: 'Qual a aula de ADS na terça?' 😊"

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
