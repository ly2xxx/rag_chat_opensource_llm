import streamlit as st
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

layout.show_header("PDF, TXT, CSV, XLSX")

uploaded_file = utils.handle_upload(["pdf", "txt", "csv", "xlsx", "zip"])

if uploaded_file:

    # Configure the sidebar
    sidebar.show_options()
    sidebar.about()

    # Initialize chat history
    history = ChatHistory()
    try:
        chatbot = utils.setup_chatbot(
            uploaded_file, st.session_state["model"], st.session_state["temperature"]
        )

        utils.setup_conversation_cockpit(layout, sidebar, history, uploaded_file, chatbot)
    except Exception as e:
        st.error(f"Error: {str(e)}")
