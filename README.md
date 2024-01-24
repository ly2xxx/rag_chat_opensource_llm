# rag_chat_opensource_llm
Experimented with Retrieval Augmented Generation based on given data

### An AI chatbot featuring conversational memory, designed to enable users to discuss their CSV, PDF, TXT data, Website page and YTB videos in a more intuitive manner. 🚀

#### For better understanding, see medium article 🖖 : [Build a chat-bot over your CSV data](https://medium.com/@yvann-hub/build-a-chatbot-on-your-csv-data-with-langchain-and-openai-ed121f85f0cd)

## Running Locally 💻
Follow these steps to set up and run the service locally :

### Prerequisites
- Python 3.9 or higher
- Git
- Ollama setup "ollama run mistral" 

### Installation
Clone the repository :
`git clone https://github.com/ly2xxx/rag_chat_opensource_llm`


Navigate to the project directory :
`cd rag_chat_opensource_llm`


Create a virtual environment :
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Install the required dependencies in the virtual environment :

`pip install -r requirements.txt`

Launch the chat service locally :

`streamlit run streamlit_app.py`

#### That's it! The AI chatbot is now up and running locally. 🤗