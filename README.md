# rag_chat_opensource_llm
Experimented with Retrieval Augmented Generation based on given data

### An AI chatbot featuring conversational memory, designed to enable users to discuss their CSV, PDF, TXT data, Website page and YTB videos in a more intuitive manner. 🚀

#### For better understanding, see medium article 🖖 : [Build a chat-bot over your CSV data](https://medium.com/@yvann-hub/build-a-chatbot-on-your-csv-data-with-langchain-and-openai-ed121f85f0cd)

## Running Locally 💻
Follow these steps to set up and run the service locally :

### Prerequisites
- Python 3.9 or higher
- Git
- Ollama setup "ollama run deepseek-v4-pro:cloud" (see https://dev.to/0xkoji/how-to-run-large-language-models-locally-on-a-windows-machine-using-wsl-and-ollama-55fd)

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

Setup gpt-2 tokenizer manually for langchain ConversationalRetrievalChain :
Copy 
`models\models--gpt2`
to
`C:\Users\[windows-username]\.cache\huggingface\hub\models--gpt2`
![gpt2 manual copy screenshot](Gallery/menu/gpt-2-setup.png?raw=true "gpt2 setup")

Launch the chat service locally :
```bash
streamlit run streamlit_app.py
```
#### That's it! The AI chatbot is now up and running locally. 🤗


![website demo screenshot](Gallery/menu/Mistral-GPU-Chat-web-2024-01-28-12_57_37.png?raw=true "website demo")

### Other resources
auto-upgrade imports - https://python.langchain.com/v0.2/docs/versions/v0_2/