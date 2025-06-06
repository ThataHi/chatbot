from flask import Flask, render_template, request
from chatbot import interpretar_mensagem

app = Flask(__name__)
historico = []  

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mensagem = request.form["mensagem"]
        resposta = interpretar_mensagem(mensagem)

        # Adiciona a nova troca ao histórico
        historico.append({
            "pergunta": mensagem,
            "resposta": resposta
        })

    return render_template("index.html", historico=historico)

if __name__ == "__main__":
    app.run(debug=True)
