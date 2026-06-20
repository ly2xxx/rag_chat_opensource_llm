import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage


class ChatHistory:
    """Conversation state backed by a single st.session_state['messages'] list.

    Each message is a dict: {"role": "user"|"assistant", "content": str}.
    Rendering uses native st.chat_message; the chain consumes the list as
    langchain_core BaseMessage objects via to_langchain_messages().
    """

    def __init__(self):
        self.messages = st.session_state.setdefault("messages", [])

    def default_prompt(self, topic):
        return f"Hello ! Ask me anything about {topic} 🤗"

    def initialize(self, uploaded_file):
        if not st.session_state["messages"]:
            self.append("assistant", self.default_prompt(uploaded_file.name))

    def reset(self, uploaded_file):
        st.session_state["messages"] = []
        self.messages = st.session_state["messages"]
        self.append("assistant", self.default_prompt(uploaded_file.name))
        st.session_state["reset_chat"] = False

    def append(self, role, content):
        st.session_state["messages"].append({"role": role, "content": content})

    def to_langchain_messages(self):
        """Prior turns as BaseMessages for the history-aware retriever."""
        converted = []
        for msg in st.session_state["messages"]:
            if msg["role"] == "user":
                converted.append(HumanMessage(content=msg["content"]))
            else:
                converted.append(AIMessage(content=msg["content"]))
        return converted

    def render(self, container=None):
        target = container if container is not None else st
        for msg in st.session_state["messages"]:
            target.chat_message(msg["role"]).write(msg["content"])
