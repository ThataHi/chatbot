import re
import requests
import sqlite3

# Definir constantes para mensagens usadas várias vezes
MENSAGEM_OLA = "Olá! Posso ajudar com informações sobre o IF Campinas."
MENSAGEM_DESCONHECIDA = "Desculpe, só respondo perguntas relacionadas ao IF Campinas."

# Sinônimos dos cursos
cursos_validos = {
    "ads": ["ads", "análise", "desenvolvimento", "sistemas"],
    "engenharia": ["engenharia", "engenharia elétrica", "eng elétrica", "eng"]
}

# Palavras-chave relacionadas à faculdade
keywords_faculdade = [
    "horário", "aula", "curso", "disciplina", "professor",
    "campinas", "if", "instituto federal", "calendário", "exame"
]

# Respostas fixas
respostas_fixas = {
    "oi": MENSAGEM_OLA,
    "olá": MENSAGEM_OLA,
    "oie": MENSAGEM_OLA,
    "quais cursos": "Os cursos superiores oferecidos incluem ADS e Engenharia Elétrica.",
    "quem são os professores": "As informações sobre professores podem variar. Consulte a coordenação do curso para mais detalhes.",
    "funcionamento": "O campus geralmente funciona de segunda a sexta, das 7h às 22h45.",
    "feriados": "Os feriados seguem o calendário acadêmico do IF Campinas.",
    "recesso": "As datas de recesso também estão no calendário acadêmico oficial."
}


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
    cumprimentos = ["oi", "olá", "bom dia",
                    "boa tarde", "boa noite", "e aí", "fala"]
    if any(cumprimento in mensagem_lower for cumprimento in cumprimentos):
        return MENSAGEM_OLA

    # Tenta identificar curso e dia da semana
    curso = identificar_curso(mensagem)
    dia_match = re.search(
        r"(segunda|terça|quarta|quinta|sexta|sábado|domingo)", mensagem_lower)

    # Quando só informa o dia
    if dia_match and not curso:
        return f"Para qual curso você quer saber o horário na {dia_match.group(1)}?"

    # Quando só informa o curso
    if curso and dia_match:
        dia = dia_match.group(1)
        return buscar_horario(curso, dia)

    # Se a mensagem tem relação com a faculdade
    if contem_palavra_faculdade(mensagem):
        # Primeiro tenta respostas fixas
        for chave in respostas_fixas:
            if chave in mensagem_lower:
                return respostas_fixas[chave]

        # Se não encontrou resposta fixa, chama o modelo de IA
        return responder_com_llm(mensagem)

    # Caso não seja nada relacionado
    return MENSAGEM_DESCONHECIDA


def buscar_horario(curso, dia):
    conn = sqlite3.connect('horarios.db')
    c = conn.cursor()
    c.execute(
        "SELECT horario, disciplina FROM horarios WHERE curso=? AND dia=?", (curso, dia))
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
        "Você é um assistente do Instituto Federal de Campinas (IF Campinas). "
        "Responda sempre em português, com frases curtas e diretas, apenas sobre assuntos relacionados ao IF Campinas, como cursos, horários e disciplinas. "
        "Não forneça dados sensíveis. "
        "Se a pergunta não for sobre esses temas, responda: 'Desculpe, só respondo perguntas relacionadas ao IF Campinas.'\n\n"
        f"Pergunta: {pergunta}\n"
        "Resposta:"
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "tinyllama", "prompt": prompt, "stream": False}
        )

        if response.ok:
            resposta = response.json().get("response", "").strip()
            return resposta if resposta else "Desculpe, não entendi."
        else:
            return f"Erro na requisição: {response.status_code}"
    except Exception as e:
        return f"Erro ao conectar ao modelo: {str(e)}"
