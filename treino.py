import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração da página para parecer App
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# Estilo CSS para interface profissional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 10px; }
    .css-1kyx60w { font-family: 'Helvetica Neue', sans-serif; }
    div.stBadge { font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('treino_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios 
                 (id INTEGER PRIMARY KEY, treino TEXT, nome TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER)''')
    
    # Pré-carregamento dos treinos se a tabela estiver vazia
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        treinos_pre_definidos = [
            # TREINO A
            ('A', '🔥 Supino Inclinado (Halter) 4x12 + Crucifixo 4x15'),
            ('A', '🔋 Pulôver (Halter) 3x15 + Desenv. 3x15'),
            ('A', '🎯 Supino Reto (Halter) 4x 8-10'),
            ('A', '💀 Tríceps Testa (Halter) 4x 8-10'),
            ('A', '💪 Tríceps Francês (Halter) 4x 8-12'),
            # TREINO B
            ('B', '⏱️ Extensora Isométrica (5 x 20s)'),
            ('B', '🦵 Extensora (3 x 15)'),
            ('B', '🚀 Leg Press Pés Afastados (4x 8-10)'),
            ('B', '🦶 Panturrilha no Leg Press (4 x 15)'),
            ('B', '💥 Leg Press Horizontal Unilateral (3x 8-10)'),
            ('B', '🎢 Cadeira Flexora (3x 8-10)'),
            ('B', '⏱️ Flexora Isometria (4 x 20s)'),
            # TREINO C
            ('C', '🛶 Remada Curvada (Barra) 4x15 + Rosca Alt. 4x15'),
            ('C', '⚔️ Remada Unilateral (Halter) 3x15 + Rosca Direta 3x15'),
            ('C', '⛓️ Remada Fechada (Barra Reta) 4x 8-10'),
            ('C', '🔨 Rosca Martelo (Halter) 4x 8-10'),
            ('C', '🎯 Rosca Concentrada (3x 8-12)'),
            # TREINO D
            ('D', '🧬 Rosca Direta 21 (7+7+7)'),
            ('D', '📉 Rosca Direta Banco Inclinado (3x 8-12)'),
            ('D', '🔼 Desenv. Sentado Neutro (4 x 8)'),
            ('D', '🦅 Elevação Lateral (3x 8-12)'),
            ('D', '💪 Tríceps Francês (Halter) 3x 8-12'),
            ('D', '🐎 Tríceps Coice (4 x 12)')
        ]
        c.executemany("INSERT INTO exercicios (treino, nome) VALUES (?, ?)", treinos_pre_definidos)
    
    conn.commit()
    conn.close()

init_db()

# --- FUNÇÕES ---
def salvar_serie(exercicio, peso, reps):
    conn = sqlite3.connect('treino_v2.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs (data, exercicio, peso, reps) VALUES (?, ?, ?, ?)",
              (datetime.now().strftime("%d/%m/%Y %H:%M"), exercicio, peso, reps))
    conn.commit()
    conn.close()

# --- INTERFACE ---
st.title("⚡ PowerLog PRO")

menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📊 Evolução", "⚙️ Gerenciar Exercícios"])

if menu == "🏋️ Treinar Agora":
    st.subheader("Bora pra cima! 🚀")
    
    col1, col2 = st.columns(2)
    with col1:
        treino_sel = st.radio("Escolha o Treino:", ["A", "B", "C", "D"], horizontal=True)
    
    conn = sqlite3.connect('treino_v2.db')
    df_ex = pd.read_sql(f"SELECT nome FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        exercicio_foco = st.selectbox("Selecione o Exercício:", df_ex['nome'])
        
        st.info(f"Registrando: {exercicio_foco}")
        
        c1, c2 = st.columns(2)
        with c1:
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5, format="%.1f")
        with c2:
            reps = st.number_input("Reps", min_value=0, step=1)
            
        if st.button("✅ Salvar Série"):
            salvar_serie(exercicio_foco, peso, reps)
            st.success(f"Série de {reps}x com {peso}kg salva!")
            st.balloons()
    else:
        st.warning("Nenhum exercício cadastrado para este treino.")

elif menu == "📊 Evolução":
    st.subheader("📈 Histórico de Cargas")
    conn = sqlite3.connect('treino_v2.db')
    df_logs = pd.read_sql("SELECT * FROM logs ORDER BY id DESC", conn)
    conn.close()
    
    if not df_logs.empty:
        st.dataframe(df_logs[['data', 'exercicio', 'peso', 'reps']], use_container_width=True)
        if st.button("🗑️ Limpar Histórico"):
             conn = sqlite3.connect('treino_v2.db')
             conn.cursor().execute("DELETE FROM logs")
             conn.commit()
             conn.close()
             st.rerun()
    else:
        st.write("Ainda não há treinos registrados.")

elif menu == "⚙️ Gerenciar Exercícios":
    st.subheader("🛠️ Personalizar Treinos")
    
    with st.expander("➕ Adicionar Novo Exercício"):
        novo_t = st.selectbox("Treino", ["A", "B", "C", "D"])
        novo_n = st.text_input("Nome do Exercício")
        if st.button("Salvar Novo"):
            conn = sqlite3.connect('treino_v2.db')
            conn.cursor().execute("INSERT INTO exercicios (treino, nome) VALUES (?, ?)", (novo_t, novo_n))
            conn.commit()
            conn.close()
            st.success("Adicionado!")
            st.rerun()

    st.divider()
    st.write("🗑️ **Excluir Exercícios Existentes:**")
    conn = sqlite3.connect('treino_v2.db')
    df_del = pd.read_sql("SELECT * FROM exercicios", conn)
    conn.close()
    
    if not df_del.empty:
        ex_para_deletar = st.selectbox("Escolha para remover:", df_del['nome'])
        if st.button("Remover"):
            conn = sqlite3.connect('treino_v2.db')
            conn.cursor().execute(f"DELETE FROM exercicios WHERE nome='{ex_para_deletar}'")
            conn.commit()
            conn.close()
            st.rerun()
