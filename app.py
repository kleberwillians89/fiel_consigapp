from flask import Flask, render_template, request, redirect, session, url_for, send_file
import json
import csv
from datetime import datetime
from io import StringIO

app = Flask(__name__)
app.secret_key = 'fiel-super-secreto'
LEADS_PATH = 'leads.json'

# ===================== PÁGINAS PÚBLICAS ========================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fgts', methods=['GET', 'POST'])
def fgts():
    if request.method == 'POST':
        salvar_lead(request.form.to_dict(), 'Saque FGTS')
        return redirect(url_for('confirmacao'))
    return render_template('fgts.html')

@app.route('/portabilidade', methods=['GET', 'POST'])
def portabilidade():
    if request.method == 'POST':
        salvar_lead(request.form.to_dict(), 'Portabilidade INSS')
        return redirect(url_for('confirmacao_portabilidade'))
    return render_template('portabilidade.html')

@app.route('/clt', methods=['GET', 'POST'])
def clt():
    if request.method == 'POST':
        salvar_lead(request.form.to_dict(), 'Empréstimo CLT')
        return redirect(url_for('confirmacao_clt'))
    return render_template('clt.html')

@app.route('/inss', methods=['GET', 'POST'])
def inss():
    if request.method == 'POST':
        salvar_lead(request.form.to_dict(), 'Empréstimo INSS')
        return redirect(url_for('confirmacao_inss'))
    return render_template('inss.html')

@app.route('/serasa', methods=['GET', 'POST'])
def serasa():
    if request.method == 'POST':
        salvar_lead(request.form.to_dict(), 'Serasa Limpa Nome')
        return redirect(url_for('confirmacao_serasa'))
    return render_template('serasa.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# ===================== CONFIRMAÇÕES ========================

@app.route('/confirmacao')
def confirmacao():
    return render_template('confirmacao.html')  # FGTS

@app.route('/confirmacao_portabilidade')
def confirmacao_portabilidade():
    return render_template('confirmacao_portabilidade.html')

@app.route('/confirmacao_clt')
def confirmacao_clt():
    return render_template('confirmacao_clt.html')

@app.route('/confirmacao_inss')
def confirmacao_inss():
    return render_template('confirmacao_inss.html')

@app.route('/confirmacao_serasa')
def confirmacao_serasa():
    return render_template('confirmacao_serasa.html')

# ===================== PAINEL ADMINISTRATIVO ========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['senha'] == 'admin123':
            session['logado'] = True
            return redirect(url_for('dashboard'))
        else:
            return 'Senha incorreta'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logado'):
        return redirect(url_for('login'))
    leads = carregar_leads()
    return render_template('dashboard.html', leads=leads)

@app.route('/importados')
def importados():
    if not session.get('logado'):
        return redirect(url_for('login'))
    try:
        with open("importados.json", "r") as f:
            lista = json.load(f)
    except:
        lista = []
    return render_template("importados.html", leads=lista)

@app.route('/importar', methods=['GET', 'POST'])
def importar():
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo.filename.endswith('.csv'):
            conteudo = arquivo.read().decode('utf-8').splitlines()
            leitor = csv.DictReader(conteudo)
            lista = []
            for linha in leitor:
                lista.append({
                    "nome": linha.get("nome", ""),
                    "telefone": linha.get("telefone", ""),
                    "cpf": linha.get("cpf", ""),
                    "servico": linha.get("produto", "")
                })
            with open("importados.json", "w") as f:
                json.dump(lista, f, indent=2)
            return redirect(url_for('importados'))

    return render_template("importar.html")

@app.route('/exportar-csv')
def exportar_csv():
    if not session.get('logado'):
        return redirect(url_for('login'))

    leads = carregar_leads()
    output = StringIO()
    fieldnames = set()
    for lead in leads:
        fieldnames.update(lead.keys())
    fieldnames = sorted(list(fieldnames))

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for lead in leads:
        writer.writerow({k: lead.get(k, '') for k in fieldnames})

    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        download_name='leads_fiel.csv',
        as_attachment=True
    )

# ===================== FUNÇÕES AUXILIARES ========================

def salvar_lead(formulario, servico):
    formulario['data'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    formulario['servico'] = servico
    leads = carregar_leads()
    leads.append(formulario)
    with open(LEADS_PATH, 'w') as f:
        json.dump(leads, f, indent=2)

def carregar_leads():
    try:
        with open(LEADS_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# ===================== RODAR APP ========================

if __name__ == '__main__':
    app.run(debug=True)
