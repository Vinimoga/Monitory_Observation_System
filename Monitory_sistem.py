import streamlit as st
import sqlite3
import pandas as pd

# Conexão ao banco de dados
def init_db():
    conn = sqlite3.connect('alunos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            origem TEXT,
            monitor TEXT,
            positivo INTEGER DEFAULT 0,
            negativo INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS observacoes (
            id INTEGER PRIMARY KEY,
            aluno_id INTEGER,
            comentario TEXT,
            tipo TEXT, -- 'positivo' ou 'negativo'
            FOREIGN KEY (aluno_id) REFERENCES alunos (id)
        )
    ''')
    conn.commit()
    return conn

# Funções para banco de dados
def adicionar_aluno(conn, nome, origem, monitor):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO alunos (nome, origem, monitor) VALUES (?, ?, ?)', (nome, origem, monitor))
    conn.commit()

def listar_alunos(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alunos')
    return cursor.fetchall()

def registrar_observacao(conn, aluno_id, comentario, tipo):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO observacoes (aluno_id, comentario, tipo) VALUES (?, ?, ?)', (aluno_id, comentario, tipo))
    conn.commit()

def buscar_observacoes(conn, aluno_id):
    cursor = conn.cursor()
    cursor.execute('SELECT comentario, tipo FROM observacoes WHERE aluno_id = ?', (aluno_id,))
    return cursor.fetchall()

# Interface Streamlit
st.title("Sistema de Observações para Alunos")

conn = init_db()

menu = st.sidebar.selectbox("Menu", ["Adicionar Aluno", "Registrar Observação", "Consultar Aluno"])

if menu == "Adicionar Aluno":
    st.subheader("Adicionar Novo Aluno")
    nome = st.text_input("Nome do Aluno")
    origem = st.selectbox("Origem", ["Campinas", "Brasília"])
    monitor = st.text_input("Monitor Responsável")
    
    if st.button("Adicionar"):
        adicionar_aluno(conn, nome, origem, monitor)
        st.success(f"Aluno {nome} adicionado com sucesso!")

elif menu == "Registrar Observação":
    st.subheader("Registrar Observação")
    alunos = listar_alunos(conn)
    alunos_dict = {f"{aluno[1]} (Monitor: {aluno[3]})": aluno[0] for aluno in alunos}
    
    aluno_selecionado = st.selectbox("Selecione o Aluno", list(alunos_dict.keys()))
    comentario = st.text_area("Escreva o comentário")
    tipo = st.radio("Tipo de Observação", ["Positivo", "Negativo"])
    
    if st.button("Salvar Observação"):
        aluno_id = alunos_dict[aluno_selecionado]
        registrar_observacao(conn, aluno_id, comentario, tipo.lower())
        st.success("Observação registrada com sucesso!")

elif menu == "Consultar Aluno":
    st.subheader("Consultar Aluno")
    alunos = listar_alunos(conn)
    alunos_dict = {f"{aluno[1]} (Monitor: {aluno[3]})": aluno[0] for aluno in alunos}
    
    aluno_selecionado = st.selectbox("Selecione o Aluno", list(alunos_dict.keys()))
    aluno_id = alunos_dict[aluno_selecionado]
    observacoes = buscar_observacoes(conn, aluno_id)
    
    st.write(f"### Observações para {aluno_selecionado}")
    for obs in observacoes:
        st.write(f"- **{obs[1].capitalize()}**: {obs[0]}")
