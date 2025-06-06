import re
import requests
import sqlite3

# Sinônimos dos cursos
cursos_validos = {
    "ads": ["ads", "análise", "desenvolvimento", "sistemas"],
    "engenharia": ["engenharia", "engenharia elétrica", "eng elétrica"]
}

# Palavras-chave relacionadas à faculdade
keywords_faculdade = [
    "horário", "aula", "curso", "disciplina", "professor",
    "campinas", "if", "instituto federal", "calendário", "exame"
]

def identificar_curso(texto):
    texto = texto.lower()
    for curso, sinonimos in cursos_validos.items():
        if any(s in texto for s in sinonimos):
            return curso
    return None

def contem_palavra_faculdade(texto):
    texto = texto.lower()
    return any(palavra in texto for palavra in keywords_faculdade)

def interpretar_mensagem(mensagem):
    mensagem_lower = mensagem.lower()

    # Respostas diretas para cumprimentos
    cumprimentos = ["oi", "olá", "bom dia", "boa tarde", "boa noite", "e aí", "fala"]
    if any(cumprimento in mensagem_lower for cumprimento in cumprimentos):
        return "Olá! Posso ajudar com informações sobre o IF Campinas."

    # Tenta identificar curso e dia
    curso = identificar_curso(mensagem)
    dia_match = re.search(r"(segunda|terça|quarta|quinta|sexta|sábado|domingo)", mensagem_lower)

    if curso and dia_match:
        dia = dia_match.group(1)
        return buscar_horario(curso, dia)

    # Se não tem curso/dia, verifica se a pergunta é sobre faculdade (keywords)
    if contem_palavra_faculdade(mensagem):
        return responder_com_llm(mensagem)

    # Caso não seja nada relacionado
    return "Desculpe, só respondo perguntas relacionadas ao IF Campinas."

def buscar_horario(curso, dia):
    conn = sqlite3.connect('horarios.db')
    c = conn.cursor()
    c.execute("SELECT horario, disciplina FROM horarios WHERE curso=? AND dia=?", (curso, dia))
    resultados = c.fetchall()
    conn.close()

    if resultados:
        resposta = f"Aulas de {curso.upper()} na {dia.capitalize()}:\n"
        for horario, disciplina in resultados:
            resposta += f"- {horario} - {disciplina}\n"
        return resposta.strip()
    else:
        return f"Não encontrei aula para {curso.upper()} na {dia.capitalize()}."

def responder_com_llm(pergunta):
    prompt = (
        "Você é um assistente virtual do Instituto Federal de Campinas (IF Campinas). "
        "Responda sempre em português, de forma clara, objetiva e com frases curtas. "
        "Você só deve responder perguntas relacionadas ao IF Campinas, como cursos, horários, disciplinas e estrutura da faculdade. "
        "Se a pergunta não estiver relacionada a esses temas, responda: 'Desculpe, só respondo perguntas relacionadas ao IF Campinas.'\n\n"
        f"Pergunta: {pergunta}\n"
        "Resposta:"
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma:2b", "prompt": prompt, "stream": False}
        )

        if response.ok:
            resposta = response.json().get("response", "").strip()

            if "Resposta:" in resposta:
                resposta = resposta.split("Resposta:")[-1].strip()

            return resposta if resposta else "Desculpe, não entendi."
        else:
            return f"Erro na requisição: {response.status_code}"
    except Exception as e:
        return f"Erro ao conectar ao modelo: {str(e)}"

