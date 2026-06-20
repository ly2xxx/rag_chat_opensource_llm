# rag_chat_opensource_llm
Experimented with Retrieval Augmented Generation based on given data

### An AI chatbot featuring conversational memory, designed to enable users to discuss their CSV, PDF, TXT data, Website page and YTB videos in a more intuitive manner. 🚀

#### For better understanding, see medium article 🖖 : [Build a chat-bot over your CSV data](https://medium.com/@yvann-hub/build-a-chatbot-on-your-csv-data-with-langchain-and-openai-ed121f85f0cd)

## Running Locally 💻
Follow these steps to set up and run the service locally :

### Prerequisites
- Python 3.11 or higher
- Git
- [uv](https://docs.astral.sh/uv/) package manager
- Ollama with a chat model (e.g. `ollama run deepseek-v4-pro:cloud`) and the embedding model `ollama pull nomic-embed-text` (see https://dev.to/0xkoji/how-to-run-large-language-models-locally-on-a-windows-machine-using-wsl-and-ollama-55fd)

### Installation
Clone the repository :
```bash
git clone https://github.com/ly2xxx/rag_chat_opensource_llm
```

Navigate to the project directory :
```bash
cd rag_chat_opensource_llm
```

Install dependencies and create a virtual environment using uv :
```bash
uv sync
```

Activate the virtual environment :
```bash
.\.venv\Scripts\activate
```

Launch the chat service locally :
```bash
streamlit run streamlit_app.py
```
#### That's it! The AI chatbot is now up and running locally. 🤗


![website demo screenshot](Gallery/menu/Mistral-GPU-Chat-web-2024-01-28-12_57_37.png?raw=true "website demo")

### Tech stack
- **LangChain 1.x** with a history-aware LCEL retrieval chain (`create_history_aware_retriever` + `create_retrieval_chain` + `create_stuff_documents_chain`)
- **Ollama** via `langchain-ollama` for both chat (`ChatOllama`) and embeddings (`OllamaEmbeddings`, `nomic-embed-text`)
- **FAISS** vector store, persisted natively with `save_local` / `load_local`
- **Streamlit** native multipage (`st.navigation`) and native chat (`st.chat_message` / `st.chat_input`)

### Other resources
- LangChain v1 migration guide - https://docs.langchain.com/oss/python/migrate/langchain-v1