import os
import pandas as pd
import streamlit as st
import pdfplumber
from io import StringIO
import re
import sys
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
    def downloadRawContent(file_name, txt):
        try:
            txt_data=txt.encode()
            st.download_button(
                    label="Download RAW content",
                    data=txt_data,
                    file_name=file_name + ".txt",
                    mime="text/plain"
            )
        except Exception as e:
            print(f"Warning - not able to offer the download RAW content: {e}")
    
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
                return shows

            def show_pdf_file(uploaded_file):
                file_container = st.expander("Your PDF file :")
                with pdfplumber.open(uploaded_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)
                return pdf_text
            
            def show_txt_file(uploaded_file):
                file_container = st.expander("Your TXT file:")
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                file_container.write(content)
                return content
            
            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()
            
            def get_file_name(uploaded_file):
                return os.path.splitext(uploaded_file)[0].lower()
            
            file_name = get_file_name(uploaded_file.name)
            file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
            if file_extension == ".csv" :
               txt = show_csv_file(uploaded_file)
            if file_extension== ".pdf" : 
                txt = show_pdf_file(uploaded_file)
            elif file_extension== ".txt" : 
                txt = show_txt_file(uploaded_file)

            Utilities.downloadRawContent(file_name, txt)

        else:
            st.session_state["reset_chat"] = True

        #print(uploaded_file)
        return uploaded_file
    
    @staticmethod
    def remove_unwanted_tags(soup):
        # Remove unwanted tags and attributes
        unwanted_tags = ['script', 'style', 'header', 'footer', 'nav', 'figure', 'figcaption']
        for tag in unwanted_tags:
            for element in soup(tag):
                element.decompose()

        return soup
    
    @staticmethod
    def clean_web_content(html_content):
        # Remove special characters and keep only alphanumeric, spaces, and certain punctuation
        clean_text = re.sub(r'[^A-Za-z0-9 \n\.\,\!\?\:\;\-\/\'\=\’]+', '', str(html_content))
        return clean_text

    @staticmethod
    def handle_webload(url, filename="raw"):
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
                soup = Utilities.remove_unwanted_tags(BeautifulSoup(response.text, 'html.parser'))

                # Extract text content from the HTML
                text_content = Utilities.clean_web_content(soup.get_text(separator='\n', strip=True))

                # Output the text content
                # print(text_content)
                file_container = st.expander("Your web page:")
                # uploaded_file.seek(0)
                # content = uploaded_file.read().decode("utf-8")
                file_container.write(text_content)
                Utilities.downloadRawContent(filename, text_content)
                return text_content

            except Exception as e:
                print(f"Error loading web page: {e}")
                return url
            
    @staticmethod
    def handle_webloads(urls, filename="raw"):
        """
        Handles and displays content from a list of web pages
        :param urls: List of URLs to load
        :return: Text content of the web pages
        """
        try:
            responses = []

            for url in urls:
                # Send a GET request to the URL
                response = requests.get(url)
                responses.append(response)

            # Use BeautifulSoup to parse the HTML content
            soups = [Utilities.remove_unwanted_tags(BeautifulSoup(response.text, 'html.parser')) for response in responses]

            # Extract text content from the HTML
            text_content = [Utilities.clean_web_content(soup.get_text(separator='\n', strip=True)) for soup in soups]

            # Output the text content
            text = ""
            file_container = st.expander("Your web pages:")
            for i, content in enumerate(text_content):
                section = f"{i+1}.{urls[i]}. {content}"
                file_container.write(section)
                text += '\n\n\n'+section

            # Download the contents of the file_container as a file
            Utilities.downloadRawContent(filename, text)

            return '\n'.join(text_content)

        except Exception as e:
            print(f"Error loading web pages: {e}")
            return urls

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
    
    @staticmethod
    def setup_conversation_cockpit(layout, sidebar, history, uploaded_file, chatbot):
        st.session_state["chatbot"] = chatbot
        sidebar.download_model(st.session_state["vectordb"])

        if st.session_state["ready"]:
            # Create containers for chat responses and user prompts
            response_container, prompt_container = st.container(), st.container()

            with prompt_container:
                # Display the prompt form
                is_ready, user_input = layout.prompt_form()

                # Initialize the chat history
                history.initialize(uploaded_file)

                # Reset the chat history if button clicked
                if st.session_state["reset_chat"]:
                    history.reset(uploaded_file)

                if is_ready:
                    # Update the chat history and display the chat messages
                    history.append("user", user_input)

                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()

                    output = st.session_state["chatbot"].conversational_chat(user_input)

                    sys.stdout = old_stdout

                    history.append("assistant", output)

                    # Clean up the agent's thoughts to remove unwanted characters
                    thoughts = captured_output.getvalue()
                    cleaned_thoughts = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', thoughts)
                    cleaned_thoughts = re.sub(r'\[1m>', '', cleaned_thoughts)

                    # Display the agent's thoughts
                    with st.expander("Display the agent's thoughts"):
                        st.write(cleaned_thoughts)

            sidebar.download_conversation(st.session_state["history"], uploaded_file.name)
            history.generate_messages(response_container)
            return True


    
