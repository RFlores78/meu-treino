import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- BANCO DE DADOS LOCAL NO TELEMÓVEL ---
def init_db():
    conn = sqlite3.connect('meu_treino_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios 
                 (nome TEXT, treino TEXT, meta TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (data TEXT, exercicio TEXT, carga REAL, reps INTEGER, nota TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- INTERFACE MOBILE ---
st.set_page_config(page_title="PowerLog", layout="centered")

st.markdown("""
    <style>
    .stButton>button { height: 70px; font-size: 20px; font-weight: bold; border-radius: 15px; }
    .stMetric { background: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.selectbox("Menu", ["Treinar Agora", "Novo Exercício", "Histórico/Evolução"])

if menu == "Treinar Agora":
    treino_dia = st.radio("Qual o treino de hoje?", ["A", "B", "C", "D"], horizontal=True)
    
    exs = pd.read_sql_query(f"SELECT * FROM exercicios WHERE treino='{treino_dia}'", conn)
    
    if exs.empty:
        st.info("Adiciona exercícios no menu lateral primeiro.")
    else:
        for _, row in exs.iterrows():
            with st.expander(f"🏋️ {row['nome']} ({row['meta']})", expanded=True):
                # Busca última carga para referência
                last = pd.read_sql_query(f"SELECT carga, nota FROM logs WHERE exercicio='{row['nome']}' ORDER BY data DESC LIMIT 1", conn)
                if not last.empty:
                    st.caption(f"Anterior: {last['carga'].iloc[0]}kg | Obs: {last['nota'].iloc[0]}")
                
                c1, c2 = st.columns(2)
                carga = c1.number_input("Kg", key=f"c_{row['nome']}", step=0.5)
                reps = c2.number_input("Reps", key=f"r_{row['nome']}", step=1)
                nota = st.text_input("Nota da série", key=f"n_{row['nome']}")
                
                if st.button(f"CONCLUIR {row['nome'].upper()}", key=f"b_{row['nome']}"):
                    dt = datetime.now().strftime("%d/%m %H:%M")
                    conn.execute("INSERT INTO logs VALUES (?,?,?,?,?)", (dt, row['nome'], carga, reps, nota))
                    conn.commit()
                    st.success("Série salva!")

elif menu == "Novo Exercício":
    st.header("Adicionar Movimento")
    n = st.text_input("Nome (ex: Leg Press)")
    t = st.selectbox("Treino", ["A", "B", "C", "D"])
    m = st.text_input("Meta (ex: 3x12)")
    if st.button("Salvar no Plano"):
        conn.execute("INSERT INTO exercicios VALUES (?,?,?)", (n, t, m))
        conn.commit()
        st.success("Exercício adicionado!")

elif menu == "Histórico/Evolução":
    st.header("📈 Evolução de Carga")
    logs = pd.read_sql_query("SELECT * FROM logs", conn)
    if not logs.empty:
        ex_sel = st.selectbox("Escolha o exercício", logs['exercicio'].unique())
        filtro = logs[logs['exercicio'] == ex_sel]
        st.line_chart(filtro.set_index('data')['carga'])
        st.table(filtro.tail(10))
