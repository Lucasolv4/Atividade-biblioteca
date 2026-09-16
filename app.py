from flask import Flask, request, redirect, render_template_string
import mysql.connector
from datetime import datetime

app = Flask(__name__)

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'biblioteca_db'
MYSQL_PORT = 3306

def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )

def inicializar_banco():
    """Garante que as tabelas existam para evitar o erro 'Table not found'"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aluno (
                cod_aluno INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                matricula VARCHAR(20) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefone VARCHAR(20)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS livro (
                cod_livro INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(150) NOT NULL,
                autor VARCHAR(100) NOT NULL,
                isbn VARCHAR(20) UNIQUE NOT NULL,
                ano_publicacao INT,
                qtd_disponivel INT NOT NULL DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emprestimo (
                cod_emprestimo INT AUTO_INCREMENT PRIMARY KEY,
                cod_aluno INT NOT NULL,
                cod_livro INT NOT NULL,
                data_emprestimo DATE NOT NULL,
                data_devolucao_prevista DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
                FOREIGN KEY (cod_aluno) REFERENCES aluno (cod_aluno) ON DELETE CASCADE,
                FOREIGN KEY (cod_livro) REFERENCES livro (cod_livro) ON DELETE CASCADE
            )
        ''')

        # Se não houver alunos, cria alguns dados iniciais
        cursor.execute('SELECT COUNT(*) FROM aluno')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO aluno (nome, matricula, email, telefone) VALUES
                ('Ana Silva', '2026001', 'ana.silva@escola.edu.br', '(64) 99999-1111'),
                ('Carlos Eduardo', '2026002', 'carlos.eduardo@escola.edu.br', '(64) 99999-2222'),
                ('Beatriz Souza', '2026003', 'beatriz.souza@escola.edu.br', '(64) 99999-3333')
            ''')

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Aviso de Inicialização: {e}")

# Run na inicialização
inicializar_banco()

# ==================== ROTAS DE LIVROS ====================

@app.route('/')
@app.route('/livros')
def listar_livros():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM livro')
    livros = cursor.fetchall()
    cursor.close()
    conn.close()

    linhas_tabela = ""
    for livro in livros:
        cod = livro.get('cod_livro') or livro.get('id_livro')
        qtd = livro.get('qtd_disponivel') if 'qtd_disponivel' in livro else livro.get('quantidade_disponivel', 0)

        linhas_tabela += f"""
        <tr>
            <td>{cod}</td>
            <td>{livro.get('titulo', '')}</td>
            <td>{livro.get('autor', '')}</td>
            <td>{livro.get('isbn', '')}</td>
            <td>{livro.get('ano_publicacao') or ''}</td>
            <td>{qtd}</td>
            <td>
                <a href="/livros/editar/{cod}">Editar</a> | 
                <form action="/livros/excluir/{cod}" method="POST" style="display:inline;">
                    <button type="submit">Excluir</button>
                </form>
            </td>
        </tr>
        """

    if not livros:
        linhas_tabela = '<tr><td colspan="7">Nenhum livro cadastrado.</td></tr>'

    with open('templates/index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_final = html_content.replace('<!-- TABELA_LIVROS -->', linhas_tabela)
    return render_template_string(html_final)

@app.route('/livros/novo', methods=['GET', 'POST'])
def criar_livro():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        isbn = request.form.get('isbn')
        ano = request.form.get('ano_publicacao') or None
        qtd = request.form.get('qtd_disponivel') or request.form.get('quantidade_disponivel') or 1

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = 'INSERT INTO livro (titulo, autor, isbn, ano_publicacao, qtd_disponivel) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, (titulo, autor, isbn, ano, qtd))
        except mysql.connector.Error:
            query = 'INSERT INTO livro (titulo, autor, isbn, ano_publicacao, quantidade_disponivel) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, (titulo, autor, isbn, ano, qtd))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/livros')

    with open('templates/cadastrar.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/livros/editar/<int:cod>', methods=['GET', 'POST'])
def editar_livro(cod):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        isbn = request.form.get('isbn')
        ano = request.form.get('ano_publicacao') or None
        qtd = request.form.get('qtd_disponivel') or request.form.get('quantidade_disponivel') or 1

        cursor_update = conn.cursor()
        try:
            query = 'UPDATE livro SET titulo=%s, autor=%s, isbn=%s, ano_publicacao=%s, qtd_disponivel=%s WHERE cod_livro=%s'
            cursor_update.execute(query, (titulo, autor, isbn, ano, qtd, cod))
        except mysql.connector.Error:
            try:
                query = 'UPDATE livro SET titulo=%s, autor=%s, isbn=%s, ano_publicacao=%s, quantidade_disponivel=%s WHERE cod_livro=%s'
                cursor_update.execute(query, (titulo, autor, isbn, ano, qtd, cod))
            except mysql.connector.Error:
                query = 'UPDATE livro SET titulo=%s, autor=%s, isbn=%s, ano_publicacao=%s, quantidade_disponivel=%s WHERE id_livro=%s'
                cursor_update.execute(query, (titulo, autor, isbn, ano, qtd, cod))

        conn.commit()
        cursor_update.close()
        cursor.close()
        conn.close()
        return redirect('/livros')

    try:
        cursor.execute('SELECT * FROM livro WHERE cod_livro = %s', (cod,))
        livro = cursor.fetchone()
    except mysql.connector.Error:
        cursor.execute('SELECT * FROM livro WHERE id_livro = %s', (cod,))
        livro = cursor.fetchone()

    cursor.close()
    conn.close()

    cod_val = livro.get('cod_livro') or livro.get('id_livro')
    qtd_val = livro.get('qtd_disponivel') if 'qtd_disponivel' in livro else livro.get('quantidade_disponivel', 0)

    with open('templates/editar.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_final = html_content.replace('VALUE_COD', str(cod_val))
    html_final = html_final.replace('VALUE_TITULO', str(livro.get('titulo', '')))
    html_final = html_final.replace('VALUE_AUTOR', str(livro.get('autor', '')))
    html_final = html_final.replace('VALUE_ISBN', str(livro.get('isbn', '')))
    html_final = html_final.replace('VALUE_ANO', str(livro.get('ano_publicacao') or ''))
    html_final = html_final.replace('VALUE_QTD', str(qtd_val))

    return render_template_string(html_final)

@app.route('/livros/excluir/<int:cod>', methods=['POST'])
def excluir_livro(cod):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM livro WHERE cod_livro = %s', (cod,))
    except mysql.connector.Error:
        cursor.execute('DELETE FROM livro WHERE id_livro = %s', (cod,))
        
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/livros')

# ==================== ROTAS DE EMPRÉSTIMOS ====================

@app.route('/emprestimos', methods=['GET'])
def listar_emprestimos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Busca os Alunos
    cursor.execute('SELECT cod_aluno, nome FROM aluno')
    alunos = cursor.fetchall()

    # Busca os Livros disponíveis (> 0)
    try:
        cursor.execute('SELECT cod_livro, titulo FROM livro WHERE qtd_disponivel > 0')
    except mysql.connector.Error:
        cursor.execute('SELECT id_livro AS cod_livro, titulo FROM livro WHERE quantidade_disponivel > 0')
    livros = cursor.fetchall()

    # Query do Histórico usando JOIN
    query_emprestimos = '''
        SELECT e.cod_emprestimo, a.nome AS aluno, l.titulo AS livro, 
               e.data_emprestimo, e.data_devolucao_prevista, e.status
        FROM emprestimo e
        JOIN aluno a ON e.cod_aluno = a.cod_aluno
        JOIN livro l ON e.cod_livro = l.cod_livro
        ORDER BY e.cod_emprestimo DESC
    '''
    try:
        cursor.execute(query_emprestimos)
        emprestimos = cursor.fetchall()
    except mysql.connector.Error:
        emprestimos = []

    cursor.close()
    conn.close()

    # Preenche o <select> de Alunos
    opcoes_alunos = "".join([f'<option value="{a["cod_aluno"]}">{a["nome"]}</option>' for a in alunos]) if alunos else '<option value="">Nenhum aluno cadastrado</option>'
    
    # Preenche o <select> de Livros
    opcoes_livros = "".join([f'<option value="{l["cod_livro"]}">{l["titulo"]}</option>' for l in livros]) if livros else '<option value="">Nenhum livro disponível</option>'

    # Preenche a Tabela
    linhas_tabela = ""
    for emp in emprestimos:
        data_emp = emp['data_emprestimo'].strftime('%d/%m/%Y') if emp['data_emprestimo'] else ''
        data_dev = emp['data_devolucao_prevista'].strftime('%d/%m/%Y') if emp['data_devolucao_prevista'] else ''
        linhas_tabela += f"""
        <tr>
            <td>{emp['cod_emprestimo']}</td>
            <td>{emp['aluno']}</td>
            <td>{emp['livro']}</td>
            <td>{data_emp}</td>
            <td>{data_dev}</td>
            <td>{emp['status']}</td>
        </tr>
        """

    if not emprestimos:
        linhas_tabela = '<tr><td colspan="6">Nenhum empréstimo registrado.</td></tr>'

    with open('templates/emprestimos.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_final = html_content.replace('<!-- OPCOES_ALUNOS -->', opcoes_alunos)
    html_final = html_final.replace('<!-- OPCOES_LIVROS -->', opcoes_livros)
    html_final = html_final.replace('<!-- TABELA_EMPRESTIMOS -->', linhas_tabela)

    return render_template_string(html_final)

@app.route('/emprestimos/novo', methods=['POST'])
def criar_emprestimo():
    cod_aluno = request.form.get('cod_aluno')
    cod_livro = request.form.get('cod_livro')
    data_devolucao = request.form.get('data_devolucao_prevista')
    data_hoje = datetime.now().strftime('%Y-%m-%d')

    if cod_aluno and cod_livro:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insere Empréstimo
        query_insert = '''
            INSERT INTO emprestimo (cod_aluno, cod_livro, data_emprestimo, data_devolucao_prevista, status)
            VALUES (%s, %s, %s, %s, 'ATIVO')
        '''
        cursor.execute(query_insert, (cod_aluno, cod_livro, data_hoje, data_devolucao))

        # Decrementa Estoque do Livro Emprestado
        try:
            query_update = 'UPDATE livro SET qtd_disponivel = qtd_disponivel - 1 WHERE cod_livro = %s'
            cursor.execute(query_update, (cod_livro,))
        except mysql.connector.Error:
            query_update = 'UPDATE livro SET quantidade_disponivel = quantidade_disponivel - 1 WHERE id_livro = %s'
            cursor.execute(query_update, (cod_livro,))

        conn.commit()
        cursor.close()
        conn.close()

    return redirect('/emprestimos')

if __name__ == '__main__':
    app.run(debug=True)