import os
import time
import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    # Reformulates a follow-up question into a standalone one using chat history,
    # so the retriever gets a self-contained query.
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question which might reference "
        "context in the chat history, formulate a standalone question which can be "
        "understood without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )

    qa_system_prompt = (
        "You are a helpful AI assistant named Robby. The user gives you a file whose "
        "content is represented by the following pieces of context, use them to answer "
        "the question.\n"
        "If you don't know the answer, just say you don't know. Do NOT try to make up "
        "an answer.\n"
        "If the question is not related to the context, search in your own knowledge "
        "base. But if you do find the answer in your own knowledge base, politely tell "
        "the user the provided context is not relevant and you have found the answer "
        "from somewhere else. And be as specific about the source of the answer as "
        "possible.\n"
        "Use as much detail as possible when responding.\n\n"
        "context: {context}"
    )

    def conversational_chat(self, query, chat_history=None):
        """
        Run a single conversational RAG turn with a history-aware retriever.

        :param query: the user's question
        :param chat_history: list of langchain_core BaseMessage from prior turns
        :return: dict with "answer", "context" (source docs) and "query_time"
        """
        start_time = time.time()
        chat_history = chat_history or []

        llm = self.initializeLLM()
        retriever = self.vectors.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", self.contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        result = rag_chain.invoke({"input": query, "chat_history": chat_history})

        result["query_time"] = time.time() - start_time
        return result

    def initializeLLM(self):
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=self.model_name, base_url=base_url, temperature=self.temperature
        )
