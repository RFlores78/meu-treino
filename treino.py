import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# Configuração da página para visual de App Profissional
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# Estilo CSS Avançado para Interface Premium
st.markdown("""
    <style>
    /* Fundo e Fonte */
    .main { background-color: #f0f2f6; font-family: 'SF Pro Display', -apple-system, sans-serif; }
    
    /* Títulos e Subtítulos */
    h1 { color: #1e1e1e; font-weight: 800; }
    h3 { color: #4a4a4a; font-weight: 600; margin-bottom: 5px; }
    
    /* Botões Principais */
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.2em; 
        background-color: #007bff; color: white; font-weight: bold; 
        border: none; box-shadow: 0px 4px 6px rgba(0,123,255,0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background-color: #0069d9; transform: translateY(-1px); }
    
    /* Inputs */
    .stNumberInput>div>div>input { border-radius: 10px; border: 1px solid #d1d1d1; }
    
    /* Cards de Métrica e Exercício */
    .ex-card { 
        background: white; padding: 25px; border-radius: 20px; 
        box-shadow: 0px 10px 20px rgba(0,0,0,0.05); text-align: center; 
        margin-bottom: 20px; border: 1px solid #e1e1e1;
    }
    .big-emoji { font-size: 80px; margin-bottom: 15px; display: block; }
    .ex-title { font-size: 22px; font-weight: 700; color: #1e1e1e; margin-bottom: 15px; }

    /* Menu Lateral */
    .css-1kyx60w { background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('treino_final.db')
    c = conn.cursor()
    # Estrutura simplificada: id, treino, nome_com_emoji
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios 
                 (id INTEGER PRIMARY KEY, treino TEXT, nome_completo TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes 
                 (id INTEGER PRIMARY KEY, data TEXT, duracao_min INTEGER, treino_tipo TEXT)''')
    
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        # Lista com emojis grandes e descritivos incorporados no nome
        treinos = [
            # TREINO A
            ('A', '🔥 Supino Inclinado + Crucifixo (4x12+4x15)'),
            ('A', '🔋 Pulôver + Desenv. (3x15+3x15)'),
            ('A', '🎯 Supino Reto (4x 8-10)'),
            ('A', '💀 Tríceps Testa (4x 8-10)'),
            ('A', '💪 Tríceps Francês (4x 8-12)'),
            # TREINO B
            ('B', '⏱️ Extensora Isométrica (5 x 20s)'),
            ('B', '🦵 Extensora (3 x 15)'),
            ('B', '🚀 Leg Press Pés Afastados (4x 8-10)'),
            ('B', '🦶 Panturrilha no Leg Press (4 x 15)'),
            ('B', '💥 Leg Horizontal Unilateral (3x 8-10)'),
            ('B', '🎢 Cadeira Flexora (3x 8-10)'),
            ('B', '⏱️ Flexora Isometria (4 x 20s)'),
            # TREINO C
            ('C', '🛶 Remada Curvada + Rosca Alternada (4x15+4x15)'),
            ('C', '⚔️ Remada Unilateral + Rosca Direta (3x15+3x15)'),
            ('C', '⛓️ Remada Fechada (4x 8-10)'),
            ('C', '🔨 Rosca Martelo (4x 8-10)'),
            ('C', '🎯 Rosca Concentrada (3x 8-12)'),
            # TREINO D
            ('D', '🧬 Rosca Direta 21 (7+7+7)'),
            ('D', '📉 Rosca Banco Inclinado (3x 8-12)'),
            ('D', '🔼 Desenv. Sentado Neutro (4x8)'),
            ('D', '🦅 Elevação Lateral (3x 8-12)'),
            ('D', '💪 Tríceps Francês (Halter) 3x 8-12'),
            ('D', ' घोड़े Tríceps Coice (4 x 12)')
        ]
        c.executemany("INSERT INTO exercicios (treino, nome_completo) VALUES (?, ?)", treinos)
    conn.commit()
    conn.close()

init_db()

# --- LÓGICA DE ESTADO ---
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = None

# --- FUNÇÕES DE AJUDA ---
def extrair_emoji(texto): return texto.split(' ')[0] if ' ' in texto else "💪"
def extrair_nome(texto): return ' '.join(texto.split(' ')[1:]) if ' ' in texto else texto

# --- INTERFACE ---
st.title("⚡ PowerLog PRO")

menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📅 Calendário & Stats", "📊 Histórico de Séries"])

if menu == "🏋️ Treinar Agora":
    st.subheader("Bora pra cima! 🚀")
    treino_sel = st.radio("Selecione o Treino:", ["A", "B", "C", "D"], horizontal=True)

    # Controle do Cronômetro (Layout em Row)
    c_cron1, c_cron2 = st.columns([2, 1])
    if st.session_state.hora_inicio is None:
        if c_cron1.button("▶️ Iniciar Treino"):
            st.session_state.hora_inicio = time.time()
            st.rerun()
    else:
        duracao_atual = int((time.time() - st.session_state.hora_inicio) / 60)
        c_cron1.warning(f"⏳ Em treino: {duracao_atual} min")
        if c_cron2.button("🏁 Finalizar"):
            tempo_total = int((time.time() - st.session_state.hora_inicio) / 60)
            conn = sqlite3.connect('treino_final.db')
            conn.cursor().execute("INSERT INTO sessoes (data, duracao_min, treino_tipo) VALUES (?, ?, ?)",
                                 (datetime.now().strftime("%Y-%m-%d"), tempo_total, treino_sel))
            conn.commit()
            conn.close()
            st.session_state.hora_inicio = None
            st.success(f"Duração: {tempo_total} min. Salvo!")
            st.balloons()
            time.sleep(2)
            st.rerun()

    st.divider()

    # Registro e Visual do Exercício
    conn = sqlite3.connect('treino_final.db')
    df_ex = pd.read_sql(f"SELECT nome_completo FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        ex_foco_completo = st.selectbox("Selecione o Exercício:", df_ex['nome_completo'])
        
        # --- CARD DO EXERCÍCIO ---
        emoji = extrair_emoji(ex_foco_completo)
        nome_limpo = extrair_nome(ex_foco_completo)
        
        st.markdown(f"""
            <div class='ex-card'>
                <span class='big-emoji'>{emoji}</span>
                <div class='ex-title'>{nome_limpo}</div>
            </div>
            """, unsafe_allow_html=True)
        # --- FIM DO CARD ---

        c1, c2 = st.columns(2)
        with c1: peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5, format="%.1f")
        with c2: reps = st.number_input("Reps", min_value=0, step=1)
            
        if st.button("✅ Salvar Série"):
            conn = sqlite3.connect('treino_final.db')
            conn.cursor().execute("INSERT INTO logs (data, exercicio, peso, reps) VALUES (?, ?, ?, ?)",
                                 (datetime.now().strftime("%d/%m/%Y %H:%M"), nome_limpo, peso, reps))
            conn.commit()
            conn.close()
            st.toast(f"Série Salva: {peso}kg")

elif menu == "📅 Calendário & Stats":
    st.subheader("📅 Seu Desempenho Anual")
    conn = sqlite3.connect('treino_final.db')
    df_sessoes = pd.read_sql("SELECT * FROM sessoes", conn)
    conn.close()
    
    if not df_sessoes.empty:
        df_sessoes['data'] = pd.to_datetime(df_sessoes['data'])
        df_ano = df_sessoes[df_sessoes['data'].dt.year == datetime.now().year]
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card' style='background:white; padding:15px; border-radius:10px; text-align:center;'><h3>{len(df_ano)}</h3><p>Dias</p></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card' style='background:white; padding:15px; border-radius:10px; text-align:center;'><h3>{round(df_ano['duracao_min'].sum()/60,1)}h</h3><p>Total</p></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card' style='background:white; padding:15px; border-radius:10px; text-align:center;'><h3>{int(df_ano['duracao_min'].mean())}m</h3><p>Média</p></div>", unsafe_allow_html=True)
            
        st.write("#### 📅 Histórico de Datas")
        df_display = df_ano[['data', 'treino_tipo', 'duracao_min']].copy()
        df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
        st.table(df_display.sort_values('data', ascending=False))

elif menu == "📊 Histórico de Séries":
    st.subheader("📈 Histórico de Cargas")
    conn = sqlite3.connect('treino_final.db')
    df_logs = pd.read_sql("SELECT data, exercicio, peso, reps FROM logs ORDER BY id DESC", conn)
    conn.close()
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.write("Nenhuma série registrada.")
