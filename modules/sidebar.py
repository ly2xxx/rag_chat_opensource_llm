import streamlit as st
import base64

class Sidebar:

    MODEL_OPTIONS = ["mistral"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

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
        with open(vectormodel, 'rb') as f:
            bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f'<a href="data:file/pkl;base64,{b64}" download=\'{vectormodel}\'>\
                Download Trained Model .pkl\
            </a> <span style="color:green; font-weight:bold;">(Combine multiple .pkl files into a .zip for deeper AI analysis later)</span>'
            st.markdown(href, unsafe_allow_html=True)

    def download_conversation(self, chathistory, chat_filename):
        # Convert the list to a string
        chat_text = "\n".join(map(str, chathistory))

        # Convert the string to bytes
        bytes_content = chat_text.encode()

        # Clean the filename by removing or replacing disallowed characters
        # clean_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', str(chathistory))

        # Create a base64-encoded link for downloading
        b64 = base64.b64encode(bytes_content).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download=\'{chat_filename}.txt\'>\
            Download Chat History .txt\
        </a> <span style="color:green; font-weight:bold;">(Combine multiple .txt files into a .zip for deeper AI analysis later)</span>'

        # Display the download link
        st.markdown(href, unsafe_allow_html=True)

    