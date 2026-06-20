import streamlit as st
import os
import shutil
import tempfile
import dotenv

class Sidebar:

    MODEL_OPTIONS = ["deepseek-v4-pro:cloud"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    #load environment variables from .env file
    dotenv.load_dotenv()

    #override defaults with .env settings
    if os.path.exists(".env") and os.environ.get("LLM_MODEL") is not None:
        MODEL_OPTIONS = os.getenv("LLM_MODEL").strip().split(",")

    @staticmethod
    def about():
        about = st.sidebar.expander("🧠 About Rob ")
        sections = [
            "#### Rob is an AI chatbot with a conversational memory, designed to allow users to discuss their data in a more intuitive way. 📄",
            "#### It uses large language models to provide users with natural language interactions about user data content. 🌐",
           ]
        for section in sections:
            about.write(section)

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
        )
        st.session_state["temperature"] = temperature
        
    def show_options(self):
        with st.sidebar.expander("🛠️ Rob's Toolkits", expanded=False):

            self.reset_chat_button()
            self.model_selector()
            self.temperature_slider()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)

    def download_model(self, vectormodel):
        # vectormodel is the folder holding the FAISS index; offer it as a zip.
        if not vectormodel or not os.path.isdir(vectormodel):
            return
        archive_base = os.path.join(tempfile.gettempdir(), os.path.basename(vectormodel))
        zip_path = shutil.make_archive(archive_base, 'zip', vectormodel)
        with open(zip_path, 'rb') as f:
            st.download_button(
                label="Download Trained Model (.zip)",
                data=f.read(),
                file_name=f"{os.path.basename(vectormodel)}.zip",
                mime="application/zip",
                help="Combine multiple index .zip files into one .zip for deeper AI analysis later",
            )

    def download_conversation(self, messages, chat_filename):
        # Build a readable transcript from the messages list of dicts
        chat_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )
        st.download_button(
            label="Download Chat History (.txt)",
            data=chat_text.encode(),
            file_name=f"{chat_filename}.txt",
            mime="text/plain",
            help="Combine multiple .txt files into a .zip for deeper AI analysis later",
        )
