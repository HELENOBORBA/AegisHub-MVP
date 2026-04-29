import streamlit as st
st.set_page_config(page_title="AegisHub", layout="wide")

import os
import re
from groq import Groq

# =========================
# 🔐 API KEY SEGURA
# =========================
api_key = None

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ API KEY não encontrada. Configure nos Secrets do Streamlit.")
    st.stop()

client = Groq(api_key=api_key)

# =========================
# 🧠 FALLBACK INTELIGENTE
# =========================
def gerar_empresas_fallback(cidade, segmento):
    return [
        {"nome": f"{segmento} Premium {cidade}", "link": "https://exemplo.com", "score": 7},
        {"nome": f"{segmento} Especialistas {cidade}", "link": "https://exemplo.com", "score": 6},
        {"nome": f"{segmento} Soluções {cidade}", "link": "https://exemplo.com", "score": 5},
    ]

# =========================
# 🔍 BUSCA DE EMPRESAS
# =========================
@st.cache_data(ttl=3600)
def buscar_empresas(cidade, segmento):

    resultados = []

    try:
        from duckduckgo_search import DDGS

        mapa_busca = {
            "Desenvolvedor de Software": ["software house", "empresa de tecnologia"],
            "Clínicas": ["clínica médica"],
            "Escritório de Contabilidade": ["contabilidade"],
            "Restaurantes": ["restaurante"],
            "Supermercados": ["supermercado"],
            "Borracharias": ["borracharia"],
            "Oficinas Mecânicas": ["oficina mecânica"]
        }

        termos = mapa_busca.get(segmento, [segmento])

        with DDGS() as ddgs:
            for termo in termos:
                query = f"{termo} em {cidade} RS empresa"

                for r in ddgs.text(query, max_results=5):
                    resultados.append({
                        "nome": r.get("title"),
                        "link": r.get("href"),
                        "score": 3
                    })

    except Exception as e:
        print("Erro na busca:", e)

    # 🔥 GARANTIA DE RESULTADO
    if not resultados:
        return gerar_empresas_fallback(cidade, segmento)

    return resultados[:5]


# =========================
# 🎯 UI
# =========================
st.title("🚀 AegisHub - Prospecção Comercial com IA")

cidade = st.text_input("Digite a cidade:")

segmentos = [
    "Oficinas Mecânicas",
    "Borracharias",
    "Supermercados",
    "Restaurantes",
    "Clínicas",
    "Escritório de Contabilidade",
    "Desenvolvedor de Software"
]

segmento = st.selectbox("Selecione o segmento:", segmentos)


# =========================
# 🚀 BOTÃO PRINCIPAL
# =========================
if st.button("Gerar Prospecção Completa"):

    if not cidade:
        st.warning("Digite a cidade")
        st.stop()

    with st.spinner("🔍 Buscando empresas..."):
        empresas = buscar_empresas(cidade, segmento)

    st.success(f"{len(empresas)} empresas identificadas")

    # =========================
    # LOOP EMPRESAS
    # =========================
    for empresa in empresas:

        st.markdown("---")

        st.markdown(f"## 🏢 {empresa['nome']}")
        st.markdown(f"🔗 {empresa['link']}")
        st.markdown(f"⭐ Score: {empresa['score']}")

        prompt = f"""
Você é um especialista em prospecção comercial B2B.

Crie uma abordagem comercial personalizada para:

Empresa: {empresa['nome']}
Segmento: {segmento}
Cidade: {cidade}

Seja direto, profissional e consultivo.
"""

        with st.spinner("🤖 Gerando proposta..."):

            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )

                proposta = response.choices[0].message.content

                # limpeza
                proposta = re.sub(r"(Telefone:.*|E-mail:.*)", "", proposta)

            except Exception as e:
                proposta = "Erro ao gerar proposta. Verifique API ou conexão."

        # =========================
        # OUTPUT
        # =========================
        st.markdown("### 📄 Proposta Comercial")
        st.markdown(proposta)

        st.code(proposta, language="text")

        mensagem = f"""
Olá {empresa['nome']},

Identifiquei uma oportunidade no segmento de {segmento} em {cidade}.

Gostaria de compartilhar algumas ideias rápidas com você.

Podemos marcar uma conversa de 15 minutos?
"""

        st.markdown("### 🎯 Mensagem pronta")
        st.code(mensagem, language="text")