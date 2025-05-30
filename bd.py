import sqlite3

def criar_banco():
    conn = sqlite3.connect('horarios.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso TEXT,
            dia TEXT,
            horario TEXT,
            disciplina TEXT
        )
    ''')

    # Dados de exemplo
    dados = [
        ('ads', 'segunda', '19h às 22h', 'Programação Web'),
        ('ads', 'terça', '19h às 22h', 'Estrutura de Dados'),
        ('engenharia', 'segunda', '08h às 11h', 'Cálculo I'),
        ('engenharia', 'terça', '08h às 11h', 'Física')
    ]

    for d in dados:
        c.execute('SELECT * FROM horarios WHERE curso=? AND dia=? AND horario=? AND disciplina=?', d)
        if not c.fetchone():
            c.execute('INSERT INTO horarios (curso, dia, horario, disciplina) VALUES (?, ?, ?, ?)', d)

    conn.commit()
    conn.close()

# Executar para criar o banco
if __name__ == "__main__":
    criar_banco()
