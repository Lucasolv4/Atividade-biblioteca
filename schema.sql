DROP DATABASE IF EXISTS biblioteca_db;
CREATE DATABASE biblioteca_db;
USE biblioteca_db;

CREATE TABLE aluno (
    cod_aluno INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    matricula VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(20)
);

CREATE TABLE livro (
    cod_livro INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    ano_publicacao INT,
    qtd_disponivel INT NOT NULL DEFAULT 1
);

CREATE TABLE emprestimo (
    cod_emprestimo INT AUTO_INCREMENT PRIMARY KEY,
    cod_aluno INT NOT NULL,
    cod_livro INT NOT NULL,
    data_emprestimo DATE NOT NULL,
    data_devolucao_prevista DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
    FOREIGN KEY (cod_aluno) REFERENCES aluno (cod_aluno) ON DELETE CASCADE,
    FOREIGN KEY (cod_livro) REFERENCES livro (cod_livro) ON DELETE CASCADE
);

INSERT INTO aluno (nome, matricula, email, telefone) VALUES
('Ana Silva', '2026001', 'ana.silva@escola.edu.br', '(64) 99999-1111'),
('Carlos Eduardo', '2026002', 'carlos.eduardo@escola.edu.br', '(64) 99999-2222'),
('Beatriz Souza', '2026003', 'beatriz.souza@escola.edu.br', '(64) 99999-3333');

INSERT INTO livro (titulo, autor, isbn, ano_publicacao, qtd_disponivel) VALUES
('Entendendo Algoritmos', 'Aditya Y. Bhargava', '9788575225639', 2017, 3),
('Clean Code', 'Robert C. Martin', '9788576082675', 2009, 2),
('O Programador Pragmático', 'Andrew Hunt', '9788575222386', 2010, 1);