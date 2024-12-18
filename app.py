from pydoc import text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas

from flask import flash, get_flashed_messages
from flask import send_file
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime, timedelta
from functools import wraps

import io
import logging
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do banco de dados
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    # Criar a tabela de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Criar a tabela de produtos com as colunas necessárias
    c.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco REAL NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    ''')
    
    # Adicionar colunas 'disponibilidade' e 'observacoes' se elas não existirem
    c.execute("PRAGMA table_info(produtos)")
    columns = [column[1] for column in c.fetchall()]
    if 'disponibilidade' not in columns:
        c.execute('ALTER TABLE produtos ADD COLUMN disponibilidade INTEGER DEFAULT 1')
        print("Coluna 'disponibilidade' adicionada com sucesso à tabela 'produtos'.")
    if 'observacoes' not in columns:
        c.execute('ALTER TABLE produtos ADD COLUMN observacoes TEXT')
        print("Coluna 'observacoes' adicionada com sucesso à tabela 'produtos'.")

    # Criar a tabela de pedidos
    c.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            produto_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            data_retirada_entrega TEXT NOT NULL,
            tipo_entrega TEXT NOT NULL,
            endereco_entrega TEXT,
            status TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Inicializar o banco de dados
init_db()

def create_empresa_table():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    # Verificar se a tabela 'empresa' existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empresa'")
    table_exists = c.fetchone()
    
    if not table_exists:
        c.execute('''
            CREATE TABLE empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                endereco TEXT,
                telefone TEXT
            )
        ''')
        conn.commit()
    
    conn.close()

create_empresa_table()

def add_empresa(nome, endereco, telefone, logo):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO empresa (nome, endereco, telefone, logo) VALUES (?, ?, ?, ?)', (nome, endereco, telefone, logo))
    conn.commit()
    conn.close()

def get_empresa():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM empresa WHERE id = 1')
    empresa = c.fetchone()
    conn.close()
    return empresa

def list_empresa_data():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    new_func(c)
    empresa = c.fetchall()
    conn.close()
    return empresa

def new_func(c):
    new_func1(c)

def new_func1(c):
    c.execute('SELECT * FROM empresa')

print(list_empresa_data())



##### Script para Verificar Colunas:

def list_columns():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("PRAGMA table_info(pedidos)")
    columns = c.fetchall()
    conn.close()
    for column in columns:
        print(column)

list_columns()



# Funções para adicionar e obter usuários
def add_user_id_column():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE pedidos ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1')  # Usar valor padrão temporariamente
        conn.commit()
        print("Coluna 'user_id' adicionada com sucesso na tabela 'pedidos'.")
    except sqlite3.OperationalError as e:
        print(f"Erro ao adicionar coluna: {e}")
    conn.close()

add_user_id_column()

def add_user(username, password):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, generate_password_hash(password)))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT id, username FROM users')
    users = c.fetchall()
    conn.close()
    return users

# Funções para produtos
def add_produto(nome, descricao, preco, ativo=1, disponibilidade=1, observacoes=""):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO produtos (nome, descricao, preco, ativo, disponibilidade, observacoes) VALUES (?, ?, ?, ?, ?, ?)', 
              (nome, descricao, preco, ativo, disponibilidade, observacoes))
    conn.commit()
    conn.close()

def get_produtos(query=None):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    if query:
        c.execute('''
            SELECT id, nome, descricao, preco, disponibilidade, observacoes 
            FROM produtos 
            WHERE nome LIKE ? OR descricao LIKE ?
        ''', ('%' + query + '%', '%' + query + '%'))
    else:
        c.execute('SELECT id, nome, descricao, preco, disponibilidade, observacoes FROM produtos')
    produtos = c.fetchall()
    conn.close()
    return produtos


def list_empresa_data():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM empresa')
    empresa = c.fetchall()
    conn.close()
    return empresa

print(list_empresa_data())



def update_db():
    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        # Verifica se a coluna 'telefone' já existe
        c.execute("PRAGMA table_info(pedidos)")
        columns = [column[1] for column in c.fetchall()]
        if 'telefone' not in columns:
            c.execute("ALTER TABLE pedidos ADD COLUMN telefone TEXT")
            print("Coluna 'telefone' adicionada com sucesso à tabela 'pedidos'.")
        else:
            print("Coluna 'telefone' já existe na tabela 'pedidos'.")
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Erro ao adicionar coluna 'telefone': {e}")

# Execute esta função uma vez para atualizar a estrutura do banco de dados
update_db()
   


def generate_all_products_pdf(produtos):
    empresa = get_empresa()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Estilos de Parágrafos
    styles = getSampleStyleSheet()
    
    # Adicionar Logotipo
    if empresa and empresa[4]:
        logo = Image(empresa[4], width=100, height=50)
        elements.append(logo)
    
    # Adicionar Dados da Empresa
    if empresa:
        header = Paragraph(f"<b>{empresa[1]}</b><br/>{empresa[2]}<br/>{empresa[3]}", styles['Normal'])
        elements.append(header)
    
    elements.append(Paragraph("<br/>", styles['Normal']))  # Adicionar espaço

    # Tabela de Produtos
    data = [['ID', 'Nome', 'Descrição', 'Preço', 'Ativo']] + [
        [produto[0], produto[1], produto[2], f'R$ {produto[3]:.2f}', 'Sim' if produto[4] else 'Não']
        for produto in produtos
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return buffer.getvalue()

def generate_pdf(pedido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 40, f"Pedido ID: {pedido['id']}")
    c.drawString(100, height - 60, f"Cliente: {pedido['cliente']}")
    c.drawString(100, height - 80, f"Telefone: {pedido['telefone']}")
    c.drawString(100, height - 100, f"Produto: {pedido['produto_nome']}")
    c.drawString(100, height - 120, f"descricao: {pedido['descricao']}")
    c.drawString(100, height - 140, f"Data de Retirada/Entrega: {pedido['data_retirada_entrega']}")
    c.drawString(100, height - 160, f"Tipo de Entrega: {pedido['tipo_entrega']}")
    c.drawString(100, height - 180, f"Endereço de Entrega: {pedido['endereco_entrega'] if pedido['endereco_entrega'] else 'N/A'}")
    c.drawString(100, height - 200, f"Status: {pedido['status']}")
    c.drawString(100, height - 220, f"Usuário: {pedido['username']}")

    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer.getvalue()











@app.route('/print_pedido/<int:pedido_id>', methods=['GET'])
def print_pedido(pedido_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''SELECT pedidos.id, pedidos.cliente, pedidos.telefone, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status, users.username
                 FROM pedidos
                 JOIN produtos ON pedidos.produto_id = produtos.id
                 JOIN users ON pedidos.user_id = users.id
                 WHERE pedidos.id = ?''', (pedido_id,))
    pedido = c.fetchone()
    conn.close()

    pedido_dict = {
        'id': pedido[0],
        'cliente': pedido[1],
        'telefone': pedido[2],
        'produto_nome': pedido[3],
        'descricao': pedido[4],
        'data_retirada_entrega': pedido[5],
        'tipo_entrega': pedido[6],
        'endereco_entrega': pedido[7],
        'status': pedido[8],
        'username': pedido[9]
    }

    pdf = generate_pdf(pedido_dict)

    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name=f"pedido_{pedido_id}.pdf")


def generate_all_pedidos_pdf(pedidos):
    empresa = get_empresa()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    # Estilos de Parágrafos
    styles = getSampleStyleSheet()
    
    # Adicionar Logotipo e Dados da Empresa
    if empresa:
        if empresa[4]:
            logo = Image(empresa[4], width=100, height=50)
            elements.append(logo)
        
        header = Paragraph(f"<b>{empresa[1]}</b><br/>{empresa[2]}<br/>{empresa[3]}", styles['Normal'])
        elements.append(header)
        elements.append(Spacer(1, 12))  # Adicionar espaço

    # Tabela de Pedidos
    data = [['ID', 'Cliente', 'Telefone', 'Produto', 'descricao', 'Data Retirada/Entrega', 'Tipo de Entrega', 'Endereço de Entrega', 'Status', 'Usuário']] + [
        [pedido[0], pedido[1], pedido[2], pedido[3], pedido[4], pedido[5], pedido[6], pedido[7] if pedido[7] else 'N/A', pedido[8], pedido[9]]
        for pedido in pedidos
    ]

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return buffer.getvalue()


def get_relatorio_por_mes_e_usuario(mes, ano, user_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''SELECT pedidos.id, pedidos.cliente, pedidos.telefone, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status, users.username
                 FROM pedidos
                 JOIN produtos ON pedidos.produto_id = produtos.id
                 JOIN users ON pedidos.user_id = users.id
                 WHERE strftime('%m', pedidos.data_retirada_entrega) = ? AND strftime('%Y', pedidos.data_retirada_entrega) = ? AND pedidos.user_id = ?''', (mes, ano, user_id))
    relatorio = c.fetchall()
    conn.close()
    return relatorio


def exemplo_concat(pedido_id, cliente):
    mensagem = "O ID do pedido é " + str(pedido_id) + " e o cliente é " + cliente
    return mensagem











### ROTAS 









@app.route('/')
def index():
    produtos = get_produtos()
    return render_template('index.html', produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('last_activity', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

# Função para verificar tempo de inatividade
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    session.modified = True
    if 'user_id' in session:
        now = datetime.now().timestamp()
        last_activity = session.get('last_activity', now)
        if now - last_activity > 60:  # 1 minuto de inatividade
            return logout()
        session['last_activity'] = now



# ###########################               Proteção de rotas
@app.route('/add_empresa', methods=['GET', 'POST'])
def add_empresa():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        logo = request.files['logo']

        if logo:
            logo_filename = secure_filename(logo.filename)
            logo.save(os.path.join('static', logo_filename))
        else:
            logo_filename = None

        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('DELETE FROM empresa')  # RemoveR dados antigos
        c.execute('INSERT INTO empresa (nome, endereco, telefone, logo) VALUES (?, ?, ?, ?)', (nome, endereco, telefone, logo_filename))
        conn.commit()
        conn.close()
        
        flash('Dados da empresa adicionados/atualizados com sucesso!', 'success')
        return redirect(url_for('imprimir'))

    return render_template('add_empresa.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/usuarios')
@login_required
def usuarios():
    users = get_all_users()  ### todos os usuários
    return render_template('usuarios.html', users=users)

@app.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(user_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if password:
            hashed_password = generate_password_hash(password)
            c.execute('''
                UPDATE users
                SET username=?, password=?
                WHERE id=?
            ''', (username, hashed_password, user_id))
        else:
            c.execute('''
                UPDATE users
                SET username=?
                WHERE id=?
            ''', (username, user_id))
        
        conn.commit()
        conn.close()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    
    c.execute('SELECT id, username FROM users WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return render_template('editar_usuario.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if get_user(username) is None:
            add_user(username, password)
            flash('Usuário registrado com sucesso!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
    return render_template('register.html')




####################                    AQUI PARTE DE PEDIDOS
@app.route('/add_pedido', methods=['GET', 'POST'])
@login_required
def add_pedido():
    if request.method == 'POST':
        cliente = request.form['cliente']
        telefone = request.form['telefone']
        produto_id = request.form['produto_id']
        descricao = request.form['descricao']
        data_retirada_entrega = request.form['data_retirada_entrega']
        tipo_entrega = request.form['tipo_entrega']
        endereco_entrega = request.form['endereco_entrega']
        status = request.form['status']
        user_id = session.get('user_id')  # Obtém o user_id da sessão de forma segura

        if not user_id:
            flash('Erro: usuário não está logado. Por favor, faça login novamente.', 'danger')
            return redirect(url_for('login'))

        save_pedido(cliente, telefone, produto_id, descricao, data_retirada_entrega, tipo_entrega, endereco_entrega, status, user_id)
        
        flash('Pedido adicionado com sucesso!', 'success')
        return redirect(url_for('pedidos_lista'))

    produtos = get_produtos()
    return render_template('add_pedido.html', produtos=produtos)

def save_pedido(cliente, telefone, produto_id, descricao, data_retirada_entrega, tipo_entrega, endereco_entrega, status, user_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO pedidos (cliente, telefone, produto_id, descricao, data_retirada_entrega, tipo_entrega, endereco_entrega, status, user_id, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (cliente, telefone, produto_id, descricao, data_retirada_entrega, tipo_entrega, endereco_entrega, status, user_id, user_id))
    conn.commit()
    conn.close()

def update_pedidos_table():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    # Verificar se as colunas 'created_by' e 'edited_by' já existem
    c.execute('PRAGMA table_info(pedidos)')
    columns = [column[1] for column in c.fetchall()]

    if 'created_by' not in columns:
        c.execute('ALTER TABLE pedidos ADD COLUMN created_by INTEGER')
    if 'edited_by' not in columns:
        c.execute('ALTER TABLE pedidos ADD COLUMN edited_by INTEGER')

    conn.commit()
    conn.close()

update_pedidos_table()



@app.route('/pedidos')
@login_required
def pedidos_lista():
    pedidos = get_pedidos()
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/atualizar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def atualizar_pedido(pedido_id):
    try:
        cliente = request.form.get('cliente')
        telefone = request.form.get('telefone')
        produto_id = int(request.form.get('produto_id'))
        descricao = request.form['descricao']
        data_retirada_entrega = request.form.get('data_retirada_entrega')
        tipo_entrega = request.form.get('tipo_entrega')
        endereco_entrega = request.form.get('endereco_entrega') if tipo_entrega == 'Entrega' else None
        status = request.form.get('status', 'Pendente')

        data_retirada_entrega = datetime.strptime(data_retirada_entrega, '%Y-%m-%dT%H:%M')

        update_pedidos_table(pedido_id, cliente, telefone, produto_id, descricao, data_retirada_entrega, tipo_entrega, endereco_entrega, status)
        return redirect(url_for('pedidos_lista'))
    except Exception as e:
        logging.error(f"Erro ao atualizar pedido: {e}")
        return str(e), 500


@app.route('/editar_pedido/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def editar_pedido(pedido_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    if request.method == 'POST':
        cliente = request.form['cliente']
        telefone = request.form['telefone']
        produto_id = request.form['produto_id']
        descricao = request.form['descricao']
        data_retirada_entrega = request.form['data_retirada_entrega']
        tipo_entrega = request.form['tipo_entrega']
        endereco_entrega = request.form['endereco_entrega']
        status = request.form['status']
        username = request.form['username']
        password = request.form['password']

        # Verificar usuário e senha
        c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        if user and check_password_hash(user[1], password):
            c.execute('''
                UPDATE pedidos
                SET cliente=?, telefone=?, produto_id=?, descricao=?, data_retirada_entrega=?, tipo_entrega=?, endereco_entrega=?, status=?, edited_by=?
                WHERE id=?
            ''', (cliente, telefone, produto_id, descricao, data_retirada_entrega, tipo_entrega, endereco_entrega, status, user[0], pedido_id))
            conn.commit()
            flash('Pedido atualizado com sucesso!', 'success')
            return redirect(url_for('view_pedido', pedido_id=pedido_id))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    c.execute('''
        SELECT pedidos.id, pedidos.cliente, pedidos.telefone, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status
        FROM pedidos
        JOIN produtos ON pedidos.produto_id = produtos.id
        WHERE pedidos.id = ?
    ''', (pedido_id,))
    pedido = c.fetchone()
    produtos = get_produtos()
    conn.close()
    return render_template('editar_pedido.html', pedido=pedido, produtos=produtos)
    
@app.route('/view_pedido/<int:pedido_id>')
@login_required
def view_pedido(pedido_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        SELECT pedidos.id, pedidos.cliente, pedidos.telefone, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status, users.username, pedidos.created_by, pedidos.edited_by
        FROM pedidos
        JOIN produtos ON pedidos.produto_id = produtos.id
        JOIN users ON pedidos.user_id = users.id
        WHERE pedidos.id = ?
    ''', (pedido_id,))
    pedido = c.fetchone()

    # Obter os nomes dos usuários que criaram e editaram o pedido
    created_by_user = get_user_by_id(pedido[10])
    edited_by_user = get_user_by_id(pedido[11]) if pedido[11] else None
    
    conn.close()
    return render_template('view_pedido.html', pedido=pedido, created_by_user=created_by_user, edited_by_user=edited_by_user)

def get_user_by_id(user_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user[0] if user else 'Usuário desconhecido'

@app.route('/imprimir_pedido/<int:pedido_id>')
@login_required
def imprimir_pedido(pedido_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        SELECT pedidos.id, pedidos.cliente, pedidos.telefone, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status, users.username
        FROM pedidos
        JOIN produtos ON pedidos.produto_id = produtos.id
        JOIN users ON pedidos.user_id = users.id
        WHERE pedidos.id = ?
    ''', (pedido_id,))
    pedido = c.fetchone()
    conn.close()
    return render_template('imprimir_pedido.html', pedido=pedido)


@app.route('/pedidos', methods=['GET', 'POST'])
@login_required
def pedidos():
    query = request.form.get('query')
    pedidos = get_pedidos(query)
    return render_template('pedidos.html', pedidos=pedidos, query=query)

def get_pedidos(query=None):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    if query:
        c.execute('''SELECT pedidos.id, pedidos.cliente, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status
                     FROM pedidos
                     JOIN produtos ON pedidos.produto_id = produtos.id
                     WHERE pedidos.cliente LIKE ? OR produtos.nome LIKE ?''', ('%' + query + '%', '%' + query + '%'))
    else:
        c.execute('''SELECT pedidos.id, pedidos.cliente, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status
                     FROM pedidos
                     JOIN produtos ON pedidos.produto_id = produtos.id''')
    pedidos = c.fetchall()
    conn.close()
    return pedidos

@app.route('/delete_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def delete_pedido(pedido_id):
    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('DELETE FROM pedidos WHERE id = ?', (pedido_id,))
        conn.commit()
        conn.close()
        flash('Pedido excluído com sucesso!', 'success')
    except Exception as e:
        logging.error(f"Erro ao excluir pedido: {e}")
        flash('Erro ao excluir pedido.', 'danger')
    return redirect(url_for('pedidos'))


@app.route('/print_all_pedidos', methods=['GET'])
@login_required
def print_all_pedidos():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''SELECT pedidos.id, pedidos.cliente, pedidos.telefone, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status, users.username
                 FROM pedidos
                 JOIN produtos ON pedidos.produto_id = produtos.id
                 JOIN users ON pedidos.user_id = users.id''')
    pedidos = c.fetchall()
    conn.close()

    pdf = generate_all_pedidos_pdf(pedidos)

    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name="todos_os_pedidos.pdf")
# 
# 
# 
# 
#                                           ### AQUI PARTE DE PRODUTOS RDS

@app.route('/cadastros')
@login_required
def cadastros():
    produtos = get_produtos()
    return render_template('cadastros.html', produtos=produtos)

@app.route('/add_produto', methods=['POST'])
@login_required
def add_produto_route():
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco = request.form.get('preco')

    add_produto(nome, descricao, preco)
    flash('Produto cadastrado com sucesso!', 'success')
    return redirect(url_for('cadastros'))

@app.route('/produtos')
@login_required
def produtos_lista():
    produtos = get_produtos()
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos', methods=['GET', 'POST'])
@login_required
def produtos():
    query = request.form.get('query')
    produtos = get_produtos(query)
    return render_template('produtos.html', produtos=produtos, query=query)


@app.route('/view_produto/<int:produto_id>')
@login_required
def view_produto(produto_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM produtos WHERE id=?', (produto_id,))
    produto = c.fetchone()
    conn.close()
    if produto:
        print(f"Produto carregado: {produto}")  # Log dos dados do produto
        return render_template('view_produto.html', produto=produto)
    else:
        flash('Produto não encontrado', 'danger')
        return redirect(url_for('produtos'))

@app.route('/editar_produto/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def editar_produto(produto_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            descricao = request.form['descricao']
            preco = request.form['preco']
            disponibilidade = request.form['ativo']  # Usar 'ativo' para consistência com o formulário
            obs = request.form['obs']
            
            print(f"nome: {nome}, descricao: {descricao}, preco: {preco}, disponibilidade: {disponibilidade}, obs: {obs}")

            if not nome and descricao in preco in disponibilidade:
                raise KeyError("Campos do formulário incompletos")

            c.execute('''
                UPDATE produtos 
                SET nome=?, descricao=?, preco=?, disponibilidade=?, observacoes=? 
                WHERE id=?
            ''', (nome, descricao, preco, disponibilidade, obs, produto_id))
            conn.commit()
            flash('Produto atualizado com sucesso!', 'success')
        except sqlite3.Error as e:
            flash(f'Erro ao atualizar produto: {str(e)}', 'danger')
            print(f'SQLite Error: {e}')
        except KeyError as e:
            flash(f'Campo ausente no formulário: {str(e)}', 'danger')
            print(f'KeyError: {e}')
        except Exception as e:
            flash(f'Erro desconhecido: {str(e)}', 'danger')
            print(f'Erro desconhecido: {e}')
        finally:
            conn.close()
        
        return redirect(url_for('produtos'))
    
    try:
        c.execute('SELECT * FROM produtos WHERE id=?', (produto_id,))
        produto = c.fetchone()
    except sqlite3.Error as e:
        flash(f'Erro ao carregar produto: {str(e)}', 'danger')
        print(f'SQLite Error: {e}')
        produto = None
    finally:
        conn.close()
    
    if produto:
        return render_template('editar_produto.html', produto=produto)
    else:
        return redirect(url_for('produtos'))


@app.route('/delete_produto/<int:produto_id>', methods=['POST'])
@login_required
def delete_produto(produto_id):
    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        conn.commit()
        conn.close()
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        logging.error(f"Erro ao excluir produto: {e}")
        flash('Erro ao excluir produto.', 'danger')
    return redirect(url_for('produtos'))



@app.route('/print_all_produtos')
@login_required
def print_all_produtos():
    produtos = get_produtos()  # Função para obter todos os produtos
    return render_template('print_all_produtos.html', produtos=produtos)

@app.route('/imprimir')
@login_required
def imprimir():
    empresa = get_empresa()
    return render_template('imprimir.html', empresa=empresa)


##### RELATORIOS

@app.route('/relatorio_por_mes_e_usuario', methods=['GET', 'POST'])
@login_required
def relatorio_por_mes_e_usuario():
    relatorio = []
    users = get_all_users()  # Função para obter todos os usuários
    produtos = get_produtos()  # Função para obter todos os produtos
    if request.method == 'POST':
        mes = request.form.get('mes', '')
        ano = request.form.get('ano', '')
        user_id = request.form.get('user_id', '')
        produto_id = request.form.get('produto_id', '')
        if mes or ano or user_id or produto_id:  # Verificar se pelo menos uma das opções foi fornecida
            relatorio = get_relatorio_por_mes_e_usuario(mes, ano, user_id, produto_id)
        else:
            # Se nenhum parâmetro for fornecido, exibe todos os pedidos
            relatorio = get_relatorio_por_mes_e_usuario(None, None, None, None)
    return render_template('relatorio_por_mes_e_usuario.html', relatorio=relatorio, users=users, produtos=produtos)

def get_all_users(): ### MOSTRAR TODOS OS USUARIOS
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT id, username FROM users')
    users = c.fetchall()
    conn.close()
    return users


def get_relatorio_por_mes_e_usuario(mes, ano, user_id, produto_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    query = '''
        SELECT pedidos.id, pedidos.cliente, pedidos.telefone, produtos.nome, pedidos.descricao, pedidos.data_retirada_entrega, pedidos.tipo_entrega, pedidos.endereco_entrega, pedidos.status, users.username, pedidos.created_by, pedidos.edited_by
        FROM pedidos
        JOIN produtos ON pedidos.produto_id = produtos.id
        JOIN users ON pedidos.user_id = users.id
        WHERE 1=1
    '''
    params = []
    if mes:
        query += ' AND strftime("%m", pedidos.data_retirada_entrega) = ?'
        params.append(mes)
    if ano:
        query += ' AND strftime("%Y", pedidos.data_retirada_entrega) = ?'
        params.append(ano)
    if user_id:
        query += ' AND pedidos.user_id = ?'
        params.append(user_id)
    if produto_id:
        query += ' AND pedidos.produto_id = ?'
        params.append(produto_id)
    c.execute(query, params)
    relatorio = c.fetchall()
    conn.close()
    return relatorio


#### EXCLUIR AS ROTAS DE IMPRESSAO EM PDF  FILTRAR O COD APP

if __name__ == '__main__':
    app.run(debug=True)
