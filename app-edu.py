import streamlit as st
import os
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURAÇÃO DA PÁGINA ---

st.set_page_config(page_title="Seu Tutor Educacional", page_icon="🧠", layout="wide")
st.title("🤖 Tutor Educacional Personalizado")
st.caption("Um sistema com 3 agentes orquestrados por um classificador para melhorar sua vida estudantil.")

# --- 2. INICIALIZAÇÃO DO MODELO (LLM) ---
try:
    llm = ChatOllama(model="llama3.2:1b", temperature=0.7)
    # Testa a conexão com o Ollama
    llm.invoke("Olá") 
except Exception as e:
    st.error(f"Erro ao conectar-se ao Ollama: {e}")
    st.error("Verifique se o Ollama está em execução no seu computador.")
    st.stop()

# --- 3. DEFINIÇÃO DOS PROMPTS DOS AGENTES ---

# AGENTE 1: O Teórico (Item 11)
prompt_agente_1 = PromptTemplate(
    template="""
    Você é um 'Tutor Teórico'. Sua especialidade é explicar conceitos de forma 
    clara, precisa e objetiva, como um livro didático.
    **NÃO** use exemplos práticos ou analogias, foque-se na definição.
    O aluno perguntou: {input}
    Explicação Teórica:
    """,
    input_variables=["input"],
)

# AGENTE 2: O Prático (Item 12)
prompt_agente_2 = PromptTemplate(
    template="""
    Você é um 'Tutor Prático'. Sua especialidade é criar exemplos práticos,
    analogias simples e casos de uso do dia-a-dia para conceitos complexos.
    **NÃO** se preocupe com a definição formal, foque-se no exemplo.
    O aluno quer um exemplo sobre: {input}
    Exemplo Prático:
    """,
    input_variables=["input"],
)

# AGENTE 4: O Gerador de Questões (O seu "fallback" inteligente)
prompt_agente_4 = PromptTemplate(
    template="""
    Você é um 'Assistente de Ensino' proativo e amigável.
    A sua função é (1) saudar o aluno, (2) criar perguntas de revisão, ou (3) gerir a conversa.
    
    TÓPICO ATUAL (com base no histórico): {topico_atual}
    PERGUNTA DO ALUNO: {input}

    Responda com base na seguinte lógica:
    1. Se o {input} for uma saudação ('Oi', 'Olá', 'Tudo bem?'), responda amigavelmente 
       e pergunte o que o aluno gostaria de estudar ou revisar.
    2. Se o {input} for um pedido de teste ('Me teste', 'Faça uma pergunta'), 
       crie uma (1) pergunta de revisão curta sobre o {topico_atual}.
    3. Para qualquer outra coisa, aja como um assistente geral.
    
    Sua Resposta:
    """,
    input_variables=["input", "topico_atual"],
)

# AGENTE 3: O ORQUESTRADOR (Item 13)
prompt_orquestrador = PromptTemplate(
    template="""
    Você é um classificador de intenção. Sua única tarefa é analisar a pergunta do usuário 
    e decidir qual agente deve respondê-la.
    
    As categorias são:
    - TEORICO: Se a pergunta pede uma definição, explicação, ou "o que é".
    - PRATICO: Se a pergunta pede um exemplo, analogia, ou "como se aplica".
    - GERADOR_QUESTOES: Se for uma saudação, um pedido de teste, ou qualquer coisa que não 
      seja teórica ou prática.

    Pergunta do Usuário: "{input}"

    Responda APENAS com a palavra da categoria (TEORICO, PRATICO, ou GERADOR_QUESTOES).
    Classificação:
    """,
    input_variables=["input"],
)

# --- 4. CONFIGURAÇÃO DAS "CADEIAS" (CHAINS) DO LANGCHAIN ---

parser = StrOutputParser()
chain_orquestrador = prompt_orquestrador | llm | parser
chain_agente_1 = prompt_agente_1 | llm | parser
chain_agente_2 = prompt_agente_2 | llm | parser
chain_agente_4 = prompt_agente_4 | llm | parser


# --- 5. LÓGICA DO CHAT (STATE E INTERFACE) ---

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu Tutor Educacional. O que vamos estudar hoje?"}
    ]
if "topico_atual" not in st.session_state:
    st.session_state.topico_atual = "Conceitos Gerais"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Orquestrador está a classificar..."):
            classificacao = chain_orquestrador.invoke({"input": user_input})
            classificacao = classificacao.strip().upper()
            st.info(f"Debug: Orquestrador classificou como: `{classificacao}`")
            
        with st.spinner(f"Agente ({classificacao}) está a pensar..."):
            if "TEORICO" in classificacao:
                st.session_state.topico_atual = user_input
                resposta = chain_agente_1.invoke({"input": user_input})
            
            elif "PRATICO" in classificacao:
                resposta = chain_agente_2.invoke({"input": user_input})
            
            else: # Fallback para GERADOR_QUESTOES
                resposta = chain_agente_4.invoke({
                    "input": user_input, 
                    "topico_atual": st.session_state.topico_atual
                })
        
        st.markdown(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
