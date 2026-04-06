import requests
from supabase import create_client, Client

# --- CONFIGURAÇÕES (Preencha com seus dados reais) ---
URL_SUPABASE = "https://ygzpwzemlnqxtgsyacum.supabase.co/"
KEY_SUPABASE = "sb_publishable_r-ri8M9o5qK0sRCEpm5hDg_9fRIoZVt"
GIPHY_API_KEY = "EBPyqTmYfdLQb53sdLXb8Sdvf0XFCHXp"

# Inicializa o cliente do Supabase
supabase: Client = create_client(URL_SUPABASE, KEY_SUPABASE)

def buscar_gif_giphy(nome_exercicio):
    """Busca o link direto do primeiro GIF no Giphy"""
    # Adicionamos 'workout' na busca para garantir que venham exercícios físicos
    query = f"{nome_exercicio} workout"
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={query}&limit=1&rating=g"
    
    try:
        response = requests.get(url).json()
        # Pega a URL da imagem fixa (fixed_height) para carregar rápido no app
        if response['data']:
            return response['data'][0]['images']['fixed_height']['url']
        return None
    except Exception as e:
        print(f"Erro na API Giphy para {nome_exercicio}: {e}")
        return None

# 1. Busca exercícios no catálogo onde a coluna gif_url está vazia (NULL)
# Certifique-se que a coluna no Supabase permite valores nulos ou está vazia
res = supabase.table("catalogo_exercicios").select("id, nome").execute()
exercicios = res.data

print(f"Iniciando atualização de {len(exercicios)} exercícios...")

# 2. Loop de atualização
for ex in exercicios:
    nome = ex['nome']
    print(f"Processando: {nome}...")
    
    link_gif = buscar_gif_giphy(nome)
    
    if link_gif:
        # Atualiza a linha específica no banco de dados
        supabase.table("catalogo_exercicios").update({"gif_url": link_gif}).eq("id", ex['id']).execute()
        print(f"✅ {nome} atualizado com sucesso!")
    else:
        print(f"⚠️ Nenhum GIF encontrado para {nome}")

print("\n🚀 Processo concluído! Verifique seu painel do Supabase.")
