import os
import hashlib
import streamlit as st
from io import StringIO
import re
import sys
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from urllib.parse import urlparse
from datetime import datetime
from st_pages import hide_pages

#To be able to update the changes made to modules in localhost (press r)
def reload_module(module_name):
    import importlib
    import sys
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]

def generate_filename(url):
    # Parse the URL to extract the domain
    domain = urlparse(url).hostname
    
    # # Format the current date and time as specified
    # current_datetime = datetime.now().strftime("%d%m%Y.%H.%M.%S")

    # Extract the last part of the URL as the filename
    path_segments = urlparse(url).path.split('/')
    last_part = path_segments[-1] if path_segments[-1] else path_segments[-2]  # Use the last non-empty segment
    
    # Generate an MD5 hash for long filenames
    if len(last_part) > 30:
        hash_object = hashlib.md5(last_part.encode())
        last_part = hash_object.hexdigest()
    
    # Format the current date
    current_date = datetime.now().strftime("%d%m%Y")
    
    # Concatenate the parts to create the filename
    filename = f"{domain}.{last_part}.{current_date}"
    
    return filename

def input_callback():
    st.session_state["reset_chat"] = True

hide_pages(["download"])
history_module = reload_module('modules.history')
layout_module = reload_module('modules.layout')
utils_module = reload_module('modules.utils')
sidebar_module = reload_module('modules.sidebar')

ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

layout.show_header("Website")

user_api_key = utils.load_api_key()

if True:

    web_url = st.text_input(placeholder="Enter Website URL", label_visibility="hidden", label =" ", on_change=input_callback)
    if len(web_url) > 0:
        web_context = utils.handle_webload(web_url)

        if web_context:

            # Configure the sidebar
            sidebar.show_options()
            sidebar.about()

            # Initialize chat history
            history = ChatHistory()
            try:
                uploaded_file = StringIO(web_context)

                web_context = web_context.strip()
                if web_context.endswith('.pkl'):
                    uploaded_file.name = web_context[:-4]
                else:
                    uploaded_file.name = generate_filename(web_url)+str(len(web_context))+".txt"

                chatbot = utils.setup_chatbot(
                    uploaded_file, st.session_state["model"], st.session_state["temperature"]
                )
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
            except Exception as e:
                st.error(f"Error: {str(e)}")


