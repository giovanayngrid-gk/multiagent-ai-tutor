import streamlit as st
import os
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seu Tutor Educacional", page_icon="🧠", layout="wide")
st.title("🤖 Tutor Educacional Personalizado")
st.caption("Um sistema com 3 agentes orquestrados por um classificador para melhorar a sua vida estudantil.")

# --- 2. INICIALIZAÇÃO DO MODELO (LLM) ---
try:
    # Temperatura reduzida para 0.2 para evitar alucinações no modelo de 1B
    llm = ChatOllama(model="llama3.2:1b", temperature=0.2)
    llm.invoke("Teste") 
except Exception as e:
    st.error(f"Erro ao conectar-se ao Ollama: {e}")
    st.error("Verifique se o Ollama está em execução no seu computador.")
    st.stop()

# --- 3. FUNÇÃO AUXILIAR DE MEMÓRIA ---
def obter_historico_recente(mensagens, limite=4):
    """Formata as últimas mensagens para dar contexto aos agentes."""
    historico_str = ""
    # Pega as últimas 'limite' mensagens (excluindo a atual que já vai no 'input')
    for msg in mensagens[-(limite+1):-1]:
        papel = "Aluno" if msg["role"] == "user" else "Tutor"
        historico_str += f"{papel}: {msg['content']}\n"
    return historico_str if historico_str else "Início da conversa."

# --- 4. DEFINIÇÃO DOS PROMPTS DOS AGENTES ---

# AGENTE 1: O Teórico
prompt_agente_1 = PromptTemplate(
    template="""Você é um Tutor Teórico especialista. Explique o tema pedido de forma clara, direta e didática.
NÃO cumprimente o aluno (não diga Olá). Vá direto à explicação teórica.

Histórico recente da conversa:
{historico}

Pedido atual do aluno: {input}

Explicação Teórica:""",
    input_variables=["input", "historico"],
)

# AGENTE 2: O Prático
prompt_agente_2 = PromptTemplate(
    template="""Você é um Tutor Prático. Crie exemplos simples do dia-a-dia e analogias fáceis para explicar o assunto.
NÃO cumprimente o aluno (não diga Olá) e não dê definições formais, foque apenas no exemplo prático.

Histórico recente da conversa:
{historico}

Pedido atual do aluno: {input}

Exemplo Prático:""",
    input_variables=["input", "historico"],
)

# AGENTE 4: O Gerador de Questões e Avaliador
prompt_agente_4 = PromptTemplate(
    template="""Você é um Assistente de Ensino avaliador. NUNCA diga 'Olá' ou 'Tudo bem?'.

Histórico recente da conversa:
{historico}

Tópico de estudo: {topico_atual}
Mensagem atual do aluno: {input}

Siga ESTRITAMENTE uma das regras abaixo conforme o contexto:
- Se o Tutor acabou de fazer uma pergunta no Histórico e a Mensagem atual do aluno for uma resposta (ex: 'A', 'B', 'C', 'D' ou tentativa de resposta), diga se ele acertou ou errou e explique o motivo de forma curta.
- Se o aluno pediu um exercício ou pergunta, crie UMA pergunta de múltipla escolha clara (com opções A, B, C, D) sobre {topico_atual}, onde apenas uma opção esteja correta.
- Se o aluno apenas informou o que quer estudar, confirme o tema e pergunte se ele prefere começar pela explicação teórica, um exemplo prático ou um exercício.

Sua Resposta:""",
    input_variables=["input", "topico_atual", "historico"],
)

# AGENTE 3: O ORQUESTRADOR
prompt_orquestrador = PromptTemplate(
    template="""Analise o histórico e a mensagem atual do aluno para escolher o agente correto.

Histórico recente:
{historico}

Mensagem atual do aluno: "{input}"

Regras de classificação:
- TEORICO: O aluno quer aprender sobre um tema, conhecer autores/conceitos, pede explicação ou diz "vamos estudar X", "quero conhecer X", "o que é X".
- PRATICO: O aluno pede um exemplo, analogia ou aplicação prática.
- GERADOR_QUESTOES: O aluno pede uma questão/teste, OU está a responder a uma pergunta feita pelo Tutor anteriormente (ex: "letra B", "A", "acho que é a C").

Responda APENAS com uma única palavra: TEORICO, PRATICO ou GERADOR_QUESTOES.
Classificação:""",
    input_variables=["input", "historico"],
)

# --- 5. CONFIGURAÇÃO DAS "CADEIAS" (CHAINS) DO LANGCHAIN ---
parser = StrOutputParser()
chain_orquestrador = prompt_orquestrador | llm | parser
chain_agente_1 = prompt_agente_1 | llm | parser
chain_agente_2 = prompt_agente_2 | llm | parser
chain_agente_4 = prompt_agente_4 | llm | parser

# --- 6. LÓGICA DO CHAT (STATE E INTERFACE) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu Tutor Educacional. O que vamos estudar hoje?"}
    ]
if "topico_atual" not in st.session_state:
    st.session_state.topico_atual = "Geral"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Obtém o histórico das últimas interações antes de chamar os modelos
    historico_formatado = obter_historico_recente(st.session_state.messages)

    with st.chat_message("assistant"):
        with st.spinner("Orquestrador está a classificar..."):
            # Se a resposta do usuário for apenas 1 letra (ex: A, B, C, D), força a rota de questões/avaliação
            if user_input.strip().upper() in ["A", "B", "C", "D", "LETRA A", "LETRA B", "LETRA C", "LETRA D"]:
                classificacao = "GERADOR_QUESTOES"
            else:
                classificacao = chain_orquestrador.invoke({
                    "input": user_input,
                    "historico": historico_formatado
                }).strip().upper()
                
            st.info(f"Debug: Orquestrador classificou como: `{classificacao}`")
            
        with st.spinner(f"Agente ({classificacao}) está a pensar..."):
            if "TEORICO" in classificacao:
                st.session_state.topico_atual = user_input
                resposta = chain_agente_1.invoke({
                    "input": user_input,
                    "historico": historico_formatado
                })
            
            elif "PRATICO" in classificacao:
                resposta = chain_agente_2.invoke({
                    "input": user_input,
                    "historico": historico_formatado
                })
            
            else:
                # Atualiza o tópico se ainda estiver no padrão inicial e a mensagem for longa
                if st.session_state.topico_atual == "Geral" and len(user_input.split()) > 2:
                    st.session_state.topico_atual = user_input
                    
                resposta = chain_agente_4.invoke({
                    "input": user_input, 
                    "topico_atual": st.session_state.topico_atual,
                    "historico": historico_formatado
                })
        
        st.markdown(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
