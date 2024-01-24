import os
import pandas as pd
import streamlit as st
import pdfplumber

from modules.chatbot import Chatbot
from modules.embedder import Embedder
import requests
from bs4 import BeautifulSoup

class Utilities:

    @staticmethod
    def load_api_key():
        """
        Loads the OpenAI API key from the .env file or 
        from the user's input and returns it
        """
        user_api_key = None
        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None
        #you can define your API key in .env directly
        # if os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
        #     user_api_key = os.environ["OPENAI_API_KEY"]
        #     st.sidebar.success("API key loaded from .env", icon="🚀")
        # else:
        #     if st.session_state.api_key is not None:
        #         user_api_key = st.session_state.api_key
        #         st.sidebar.success("API key loaded from previous input", icon="🚀")
        #     else:
        #         user_api_key = st.sidebar.text_input(
        #             label="#### Your OpenAI API key👇\n(Don't worry, we don't store your key ever !)", placeholder="sk-...", type="password"
        #         )
        #         if user_api_key:
        #             st.session_state.api_key = user_api_key

        return user_api_key

    
    @staticmethod
    def handle_upload(file_types):
        """
        Handles and display uploaded_file
        :param file_types: List of accepted file types, e.g., ["csv", "pdf", "txt"]
        """
        uploaded_file = st.sidebar.file_uploader("upload", type=file_types, label_visibility="collapsed")
        if uploaded_file is not None:

            def show_csv_file(uploaded_file):
                file_container = st.expander("Your CSV file :")
                uploaded_file.seek(0)
                shows = pd.read_csv(uploaded_file)
                file_container.write(shows)

            def show_pdf_file(uploaded_file):
                file_container = st.expander("Your PDF file :")
                with pdfplumber.open(uploaded_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)
            
            def show_txt_file(uploaded_file):
                file_container = st.expander("Your TXT file:")
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                file_container.write(content)
            
            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()
            
            file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
            #if file_extension == ".csv" :
            #    show_csv_file(uploaded_file)
            if file_extension== ".pdf" : 
                show_pdf_file(uploaded_file)
            elif file_extension== ".txt" : 
                show_txt_file(uploaded_file)

        else:
            st.session_state["reset_chat"] = True

        #print(uploaded_file)
        return uploaded_file
    
    @staticmethod
    def handle_webload(url):
            """
            Handles and displays content from a web page
            :param url: URL of the web page to load
            :return: Text content of the web page
            """
            try:
                # Send a GET request to the URL
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for bad responses

                # Use BeautifulSoup to parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract text content from the HTML
                text_content = soup.get_text(separator='\n', strip=True)

                # Output the text content
                # print(text_content)
                file_container = st.expander("Your web page:")
                # uploaded_file.seek(0)
                # content = uploaded_file.read().decode("utf-8")
                file_container.write(text_content)

                return text_content

            except Exception as e:
                print(f"Error loading web page: {e}")
                return url

    @staticmethod
    def setup_chatbot(uploaded_file, model, temperature):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embeds = Embedder()

        with st.spinner("Processing..."):
            uploaded_file.seek(0)
            file = uploaded_file.read()
            # Get the document embeddings for the uploaded file
            vectors = embeds.getDocEmbeds(file, uploaded_file.name)

            # Create a Chatbot instance with the specified model and temperature
            chatbot = Chatbot(model, temperature,vectors)
        st.session_state["ready"] = True

        return chatbot


    
