import streamlit as st
st.set_page_config(page_title="AegisHub", layout="wide")

import os
import re
import requests
from groq import Groq

# =========================
# 🔐 CONFIGURAÇÃO DE APIS
# =========================

# 👉 Google = empresas reais
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

# 👉 Groq = inteligência (texto)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

st.write("Google API carregada:", bool(GOOGLE_API_KEY))
st.write("Groq API carregada:", bool(GROQ_API_KEY))

# =========================
# 🚨 VALIDAÇÃO
# =========================

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY não encontrada.")
    st.stop()

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY não encontrada.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =========================
# 🔍 BUSCA EMPRESAS (GOOGLE)
# =========================
@st.cache_data(ttl=3600)
def buscar_empresas(cidade, segmento):

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    query = f"{segmento} em {cidade}"

    params = {
        "query": query,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    resultados = []

    for r in data.get("results", [])[:5]:

        resultados.append({
            "nome": r.get("name"),
            "rating": r.get("rating"),
            "endereco": r.get("formatted_address"),
            "maps": f"https://www.google.com/maps/place/?q=place_id:{r.get('place_id')}"
        })

    return resultados


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
# 🚀 EXECUÇÃO
# =========================
if st.button("Gerar Prospecção Completa"):

    if not cidade:
        st.warning("Digite a cidade")
        st.stop()

    with st.spinner("🔍 Buscando empresas reais no Google..."):
        empresas = buscar_empresas(cidade, segmento)

    if not empresas:
        st.error("❌ Nenhuma empresa encontrada.")
        st.stop()

    st.success(f"{len(empresas)} empresas encontradas")

    # =========================
    # LOOP EMPRESAS
    # =========================
    for empresa in empresas:

        st.markdown("---")

        st.markdown(f"## 🏢 {empresa['nome']}")

        if empresa.get("rating"):
            st.markdown(f"⭐ Avaliação: {empresa['rating']}")

        if empresa.get("endereco"):
            st.markdown(f"📍 {empresa['endereco']}")

        st.markdown(f"🗺️ [Ver no Google Maps]({empresa['maps']})")

        # =========================
        # 🤖 PROMPT IA
        # =========================
        prompt = f"""
Você é um especialista em prospecção comercial B2B.

Crie uma abordagem comercial personalizada para:

Empresa: {empresa['nome']}
Segmento: {segmento}
Cidade: {cidade}

Regras:
- Não inventar dados da empresa
- Ser direto, profissional e consultivo
"""

        with st.spinner("🤖 Gerando proposta..."):

            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )

                proposta = response.choices[0].message.content

                proposta = re.sub(r"(Telefone:.*|E-mail:.*)", "", proposta)

            except Exception as e:
                st.error("Erro na IA")
                st.exception(e)
                proposta = "❌ Falha ao gerar proposta."

        st.markdown("### 📄 Proposta Comercial")
        st.markdown(proposta)

        # =========================
        # 📩 MENSAGEM PRONTA
        # =========================
        mensagem = f"""
Olá {empresa['nome']},

Analisei sua empresa no segmento de {segmento} em {cidade} e identifiquei oportunidades interessantes de melhoria e crescimento.

Gostaria de compartilhar algumas ideias rápidas com você.

Podemos conversar por 15 minutos?
"""

        st.markdown("### 🎯 Mensagem pronta")
        st.code(mensagem)