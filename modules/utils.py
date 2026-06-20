import os
import pandas as pd
import streamlit as st
import pdfplumber
import re
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

              def show_excel_file(uploaded_file):
                  file_container = st.expander("Your Excel file :")
                  uploaded_file.seek(0)
                  df = pd.read_excel(uploaded_file)
                  # Convert all columns to string type for consistent display
                  df = df.astype(str)
                  file_container.write(df)
                  return df.to_string()
            
              def get_file_extension(uploaded_file):
                  return os.path.splitext(uploaded_file)[1].lower()
            
              def get_file_name(uploaded_file):
                  return os.path.splitext(uploaded_file)[0].lower()
            
              file_name = get_file_name(uploaded_file.name)
              file_extension = get_file_extension(uploaded_file.name)

              # Show the contents of the file based on its extension
              txt = None
              if file_extension == ".csv" :
               txt = show_csv_file(uploaded_file)
              if file_extension== ".pdf" : 
                  txt = show_pdf_file(uploaded_file)
              if file_extension== ".txt" : 
                  txt = show_txt_file(uploaded_file)
              if file_extension == ".xlsx":
                  txt = show_excel_file(uploaded_file)

            #   if txt and len(txt)>0:            
            #       if txt is not None and (isinstance(txt, str) or not txt.empty):
            #           Utilities.downloadRawContent(file_name, txt)
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

        if not st.session_state.get("ready"):
            return None

        # Initialize / reset the chat history
        history.initialize(uploaded_file)
        if st.session_state.get("reset_chat"):
            history.reset(uploaded_file)

        # Render the existing conversation
        history.render()

        # Native chat input for the next question
        user_input = st.chat_input("Ask me anything about the document...")
        if user_input:
            history.append("user", user_input)
            st.chat_message("user").write(user_input)

            # Chat history excludes the question we just appended
            prior = history.to_langchain_messages()[:-1]
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = chatbot.conversational_chat(user_input, prior)
                answer = result["answer"]
                st.write(answer)
                with st.expander("Sources"):
                    for doc in result.get("context", []):
                        st.markdown(
                            f"- *{doc.metadata.get('source', 'document')}*: "
                            f"{doc.page_content[:300]}..."
                        )
                st.caption(f"Query time: {result['query_time']:.2f} seconds")

            history.append("assistant", answer)

        sidebar.download_conversation(st.session_state["messages"], uploaded_file.name)
        return True


    
