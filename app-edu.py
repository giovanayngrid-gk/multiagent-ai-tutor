import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Seu Tutor Educacional", page_icon="🧠", layout="wide")
st.title("🤖 Tutor Educacional Personalizado")
st.caption("Um sistema com 3 agentes orquestrados por um classificador para melhorar a sua vida estudantil.")

# --- 2. INICIALIZAÇÃO DO MODELO (LLM) ---
try:
    llm = ChatOllama(model="llama3.2:1b", temperature=0.3)
    llm.invoke("Oi")
except Exception as e:
    st.error(f"Erro ao conectar-se ao Ollama: {e}")
    st.stop()

parser = StrOutputParser()

# --- 3. PROMPTS ESTRUTURADOS (CHAT NATIVO PARA NÃO VAZAR TEXTO) ---

# AGENTE 1: Teórico
prompt_teorico = ChatPromptTemplate.from_messages([
    ("system", "És um professor de {topico}. Explica o que o aluno pediu de forma clara, direta e didática em português. Não faças perguntas de múltipla escolha."),
    MessagesPlaceholder(variable_name="historico"),
    ("human", "{input}")
])

# AGENTE 2: Prático
prompt_pratico = ChatPromptTemplate.from_messages([
    ("system", "És um professor prático de {topico}. Dá apenas um exemplo prático do dia a dia ou uma analogia simples para explicar o que o aluno pediu."),
    MessagesPlaceholder(variable_name="historico"),
    ("human", "{input}")
])

# AGENTE 4A: Criador de Questões
prompt_criar_questao = ChatPromptTemplate.from_messages([
    ("system", "És um professor de {topico}. Cria apenas UMA pergunta de múltipla escolha sobre o tema da conversa com 4 opções (A, B, C, D). Não reveles a resposta certa agora."),
    MessagesPlaceholder(variable_name="historico"),
    ("human", "{input}")
])

# AGENTE 4B: Avaliador de Resposta
prompt_avaliar = ChatPromptTemplate.from_messages([
    ("system", "Olha para a última pergunta feita na conversa. O aluno respondeu '{input}'. Diz se a opção está correta ou incorreta e explica o porquê em duas frases."),
    MessagesPlaceholder(variable_name="historico"),
    ("human", "{input}")
])

# ORQUESTRADOR SIMPLIFICADO (Para o modelo 1B não se perder)
prompt_orquestrador = ChatPromptTemplate.from_messages([
    ("system", "Classifica a frase do aluno numa única palavra: TEORICO (se quer aprender ou entender um assunto), PRATICO (se pede exemplo) ou QUESTAO (se pede exercício/teste). Responde só com uma palavra."),
    ("human", "{input}")
])

chain_teorico = prompt_teorico | llm | parser
chain_pratico = prompt_pratico | llm | parser
chain_questao = prompt_criar_questao | llm | parser
chain_avaliar = prompt_avaliar | llm | parser
chain_orquestrador = prompt_orquestrador | llm | parser

# --- 4. FUNÇÕES AUXILIARES ---
def formatar_historico_langchain(mensagens, limite=4):
    """Converte o histórico do Streamlit para objetos nativos do LangChain."""
    hist = []
    for msg in mensagens[-(limite+1):-1]:
        if msg["role"] == "user":
            hist.append(HumanMessage(content=msg["content"]))
        else:
            hist.append(AIMessage(content=msg["content"]))
    return hist

def classificar_intencao(texto_usuario):
    """Orquestrador Híbrido: Regras rápidas + LLM de fallback para garantir precisão no modelo 1B."""
    t = texto_usuario.strip().lower()
    
    # 1. Verifica se é resposta a um exercício (A, B, C, D)
    if t in ["a", "b", "c", "d", "letra a", "letra b", "letra c", "letra d"] or t.startswith("resposta"):
        return "AVALIADOR_QUESTOES"
    
    # 2. Verifica se pede exemplo prático
    if any(p in t for p in ["exemplo", "prático", "pratico", "analogia", "cotidiano", "dia a dia"]):
        return "PRATICO"
        
    # 3. Verifica se pede teste/questão
    if any(p in t for p in ["teste", "pergunta", "questão", "questao", "exercício", "exercicio", "quiz"]):
        return "GERADOR_QUESTOES"
        
    # 4. Verifica se quer estudar/entender teoria
    if any(p in t for p in ["estudar", "entender", "conhecer", "explica", "o que é", "quem foi", "quem foram", "filosofia", "sobre"]):
        return "TEORICO"
        
    # 5. Caso contrário, usa o LLM Orquestrador
    res = chain_orquestrador.invoke({"input": texto_usuario}).strip().upper()
    if "PRATICO" in res:
        return "PRATICO"
    elif "QUEST" in res:
        return "GERADOR_QUESTOES"
    return "TEORICO"

# --- 5. INTERFACE E ESTADO DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o teu Tutor Educacional. Que tema vamos estudar hoje?"}
    ]
if "topico_atual" not in st.session_state:
    st.session_state.topico_atual = "Conhecimentos Gerais"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    historico_lc = formatar_historico_langchain(st.session_state.messages)

    with st.chat_message("assistant"):
        with st.spinner("Orquestrador está a classificar..."):
            classificacao = classificar_intencao(user_input)
            st.info(f"Debug: Orquestrador classificou como: `{classificacao}`")

        with st.spinner(f"Agente ({classificacao}) está a pensar..."):
            # Atualiza o tópico quando o aluno introduz um assunto novo na rota teórica
            if classificacao == "TEORICO" and len(user_input.split()) >= 2:
                st.session_state.topico_atual = user_input

            dados = {
                "input": user_input,
                "topico": st.session_state.topico_atual,
                "historico": historico_lc
            }

            if classificacao == "TEORICO":
                resposta = chain_teorico.invoke(dados)
            elif classificacao == "PRATICO":
                resposta = chain_pratico.invoke(dados)
            elif classificacao == "AVALIADOR_QUESTOES":
                resposta = chain_avaliar.invoke(dados)
            else:
                resposta = chain_questao.invoke(dados)

        st.markdown(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
