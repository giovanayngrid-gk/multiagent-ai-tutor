# 🤖 Multi-Agent AI Study Assistant

> Sistema inteligente baseado em arquitetura multiagente para automação, curadoria e aceleração de estudos acadêmicos e técnicos utilizando LLMs.

---

## 📌 Contexto e Solução
Estudar tópicos complexos exige organização de cronograma, síntese de referências, elaboração de questionários e resolução de dúvidas. 

Este projeto orquestra múltiplos agentes autônomos de IA, onde cada agente assume uma persona e responsabilidade específica no fluxo de aprendizagem:

```text
[Objetivo de Estudo / Tema do Usuário]
                 │
                 ▼
     [Agente Curador / Pesquisador]  ──▶ Mapeia tópicos essenciais e referências
                 │
                 ▼
     [Agente Professor / Síntese]    ──▶ Estrutura explicações conceituais e exemplos
                 │
                 ▼
     [Agente Avaliador / Quiz]       ──▶ Gera flashcards, questões práticas e métricas

```

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Framework Multiagente:** CrewAI / LangGraph / Autogen
* **Modelos de Linguagem:** OpenAI API (GPT) / Google Gemini API / Ollama
* **Orquestração e Prompts:** LangChain / Pydantic
* **Ambiente / Interface:** Terminal / Streamlit

---

## 👥 Especialização dos Agentes

* **Agente Pesquisador:** Varre o conteúdo-base ou documentações para delimitar o escopo pedagógico.
* **Agente Didático:** Sintetiza os conceitos em módulos estruturados, analogias e resumos executivos.
* **Agente Mentor & Avaliador:** Formula testes práticos e valida o entendimento do usuário através de feedback iterativo.

---

## 🚀 Como Executar o Projeto

1. Clone o repositório:

```bash
git clone [https://github.com/giovanayngrid-gk/multiagent-study-assistant.git](https://github.com/giovanayngrid-gk/multiagent-study-assistant.git)
cd multiagent-study-assistant

```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

```

3. Instale as dependências:

```bash
pip install -r requirements.txt

```

4. Configure a chave de API no arquivo `.env`:

```bash
OPENAI_API_KEY=sua_chave_aqui
# ou GEMINI_API_KEY=sua_chave_aqui

```

5. Execute a equipe de agentes:

```bash
python main.py

```

---

## 👩‍💻 Autora

* **Giovana Yngrid Duarte Ribeiro**
