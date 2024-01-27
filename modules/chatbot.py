import streamlit as st
from langchain.chat_models import ChatOllama
from langchain.chains import ConversationalRetrievalChain
# from langchain.chains import RetrievalQA
from langchain.prompts.prompt import PromptTemplate
import time
# from langchain.callbacks import get_openai_callback
# from ctransformers import AutoModelForCausalLM
# from transformers import AutoTokenizer, BitsAndBytesConfig
# from langchain.llms import HuggingFacePipeline
# import torch
# import transformers

#fix Error: module 'langchain' has no attribute 'verbose'
import langchain
langchain.verbose = False

class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    qa_template = """
        You are a helpful AI assistant named Robby. The user gives you a file its content is represented by the following pieces of context, use them to answer the question at the end.
        If you don't know the answer, just say you don't know. Do NOT try to make up an answer.
        If the question is not related to the context, politely respond that you are tuned to only answer questions that are related to the context.
        Use as much detail as possible when responding.

        context: {context}
        =========
        question: {question}
        ======
        """

    QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["context","question" ])

    def conversational_chat(self, query):
        start_time = time.time()
        """
        Start a conversational chat with a model via Langchain
        """
        llm = self.initializeLLM()

        retriever = self.vectors.as_retriever(search_type="similarity", search_kwargs={"k":3})

        chain = ConversationalRetrievalChain.from_llm(llm=llm,
            retriever=retriever, verbose=True, return_source_documents=True, max_tokens_limit=4097, combine_docs_chain_kwargs={'prompt': self.QA_PROMPT})
        
        chain_input = {"question": query, "chat_history": st.session_state["history"]}
        result = chain(chain_input)
        st.session_state["history"].append((query, result["answer"]))

        end_time = time.time()
        execution_time = end_time - start_time
        
        return result["answer"]+"\n------\n"+f"Query time: {execution_time:.4f} seconds"

        #https://medium.com/@onkarmishra/using-langchain-for-question-answering-on-own-data-3af0a82789ed
        # qa_chain = RetrievalQA.from_chain_type(
        #     llm,
        #     retriever=retriever,
        #     chain_type="map_reduce",
        #     return_source_documents=True
        #     # chain_type_kwargs={"prompt": self.QA_PROMPT}
        # )

        # result = qa_chain({"query": query})

        # st.session_state["history"].append((query, result["result"]))
        # st.session_state["history"].append((query, result["source_documents"][0]))
        
        # end_time = time.time()
        # execution_time = end_time - start_time

        # return result["result"]+"\n------\n"+f"Query time: {execution_time:.4f} seconds"

    def initializeLLM(self):
        llm = ChatOllama(model=self.model_name, temperature=self.temperature)
   
        # model = AutoModelForCausalLM.from_pretrained(
        #     "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
        #     model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        #     model_type="mistral", 
        #     gpu_layers=0, hf=True,
        #     max_new_tokens = 1000,
        #     context_length = 6000
        # )
        # tokenizer = AutoTokenizer.from_pretrained(
        #     "mistralai/Mistral-7B-v0.1", 
        #     use_fast=True
        # )

        # # Create a pipeline
        # pipeline = transformers.pipeline(model=model, tokenizer=tokenizer, max_new_tokens=2048, task='text-generation')

        # llm = HuggingFacePipeline(
        #     pipeline=pipeline,
        #     )

        return llm


# def count_tokens_chain(chain, query):
#     with get_openai_callback() as cb:
#         result = chain.run(query)
#         st.write(f'###### Tokens used in this conversation : {cb.total_tokens} tokens')
#     return result 

    
    
