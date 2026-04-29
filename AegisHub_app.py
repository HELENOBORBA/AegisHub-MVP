import streamlit as st
st.set_page_config(page_title="AegisHub", layout="wide")

import os
import re
from groq import Groq
from duckduckgo_search import DDGS

# 🔐 API KEY
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("❌ API KEY não encontrada")
    st.stop()

client = Groq(api_key=api_key)

# 🚀 CACHE (não refaz busca toda hora)
@st.cache_data(ttl=3600)
def buscar_empresas(cidade, segmento):

    mapa_busca = {
        "Desenvolvedor de Software": ["software house", "empresa de tecnologia"],
        "Clínicas": ["clínica médica", "clínica saúde"],
        "Escritório de Contabilidade": ["contabilidade", "escritório contábil"],
        "Restaurantes": ["restaurante"],
        "Supermercados": ["supermercado"],
        "Borracharias": ["borracharia"],
        "Oficinas Mecânicas": ["oficina mecânica"]
    }

    termos = mapa_busca.get(segmento, [segmento])

    bloqueados = [
        "curso","faculdade","tutorial","blog",
        "download","what is","o que é","guia",
        "tradução","translation"
    ]

    bloqueio_dominios = [
        "olx","mercadolivre","amazon",
        "wikipedia","youtube","facebook",
        "instagram","linkedin"
    ]

    resultados = []

    try:
        with DDGS() as ddgs:

            for termo in termos:
                query = f"{termo} em {cidade} RS empresa"

                for r in ddgs.text(query, max_results=10):

                    titulo = r.get("title", "").lower()
                    link = r.get("href", "").lower()

                    if any(b in titulo for b in bloqueados):
                        continue

                    if any(b in link for b in bloqueio_dominios):
                        continue

                    score = 0

                    if cidade.lower() in titulo:
                        score += 2

                    if ".com.br" in link:
                        score += 2

                    if "empresa" in titulo or "serviços" in titulo:
                        score += 2

                    if score >= 2:
                        resultados.append({
                            "nome": r.get("title"),
                            "link": r.get("href"),
                            "score": score
                        })

    except Exception as e:
        print("Erro:", e)

    if not resultados:
        with DDGS() as ddgs:
            for r in ddgs.text(f"{segmento} {cidade} empresa", max_results=5):
                resultados.append({
                    "nome": r.get("title"),
                    "link": r.get("href"),
                    "score": 1
                })

    vistos = set()
    unicos = []
    for r in resultados:
        if r["link"] not in vistos:
            unicos.append(r)
            vistos.add(r["link"])

    return sorted(unicos, key=lambda x: x["score"], reverse=True)[:5]


# 🎯 UI
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


# 🚀 BOTÃO PRINCIPAL
if st.button("Gerar Prospecção Completa"):

    if not cidade:
        st.warning("Digite a cidade")
        st.stop()

    with st.spinner("🔍 Buscando empresas de alta qualidade..."):
        empresas = buscar_empresas(cidade, segmento)

    if not empresas:
        st.warning("Nenhuma empresa encontrada.")
        st.stop()

    st.success(f"{len(empresas)} empresas encontradas")

    for empresa in empresas:

        with st.container():

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

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )

                proposta = response.choices[0].message.content

                proposta = re.sub(r"(Telefone:.*|E-mail:.*)", "", proposta)

                st.markdown("### 📄 Proposta")
                st.markdown(proposta)

                # 🔥 BOTÃO COPIAR
                st.code(proposta, language="text")

                st.markdown("### 🎯 Abordagem pronta")

                mensagem = f"""
Olá {empresa['nome']},

Identifiquei uma oportunidade interessante no segmento de {segmento} em {cidade}.

Gostaria de compartilhar algumas ideias rápidas com você.

Podemos marcar uma conversa de 15 minutos?
"""

                st.code(mensagem, language="text")

            st.markdown("---")