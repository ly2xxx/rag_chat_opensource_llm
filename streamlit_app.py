import streamlit as st
from PIL import Image
import os


def generate_thumbnail(image_path, thumbnail_size=(500, 500)):
    original_image = Image.open(image_path)
    thumbnail = original_image.resize(thumbnail_size)
    return thumbnail


def render_home():
    # Contact
    with st.sidebar.expander("📬 Contact"):
        st.write(
            "**GitHub:**",
            "[Open-Source LLM solution](https://github.com/ly2xxx/rag_chat_opensource_llm/)",
        )
        st.write("**Blog:** " "[@ly2xxx](https://edisonideas.wordpress.com/)")
        st.write("**Mail** : ly2xxx@hotmail.com")

    # Title
    st.markdown(
        """
        <h2 style='text-align: center;'>Rob, your data-aware research assistant 🤖</h2>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    mascot_image_file = "Gallery/mascot/01_mascot.jpeg"
    thumbnail = generate_thumbnail(mascot_image_file)
    st.image(thumbnail, caption="Rob", width="stretch")

    # Description
    typing_script = """
    <style>
        #typed-text {
            overflow: hidden;
            white-space: nowrap; /* Set to nowrap to prevent line breaks */
            border-right: .15em solid orange;
            font-size: 13px; /* Adjust font size as needed */
            margin: 0 auto;
            letter-spacing: .15em;
            animation: typing 6s steps(100, end), blink-caret .5s step-end infinite;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: orange; }
        }
    </style>

    <div id="typed-text">Ever felt like you've wasted hours of time wading through documents on the internet?</div>

    <script>
        function removeAnimation() {
            document.getElementById("typed-text").style.animation = "none";
        }
        document.getElementById("typed-text").addEventListener("animationend", removeAnimation);
    </script>
    """
    st.markdown(typing_script, unsafe_allow_html=True)
    st.markdown(
        """
        <h9 style='text-align:left;'>- What if..you had a tireless personal assistant that could pre-analyze all your documents, websites, and videos, highlighting the parts that are most relevant to your needs?</h9>
        <br/>
        <h9 style='text-align:left;'>- So that, this digital assistant could be your secret weapon for staying on top of your workload and staying informed, saving you time and effort by identifying the most important information for you.</h9>
        <h5 style='text-align:center;'>I'm Rob, an intelligent chatbot created for exactly this purpose, by combining
        the strengths of VectorDB, Langchain and Streamlit. I use Retrieval-augmented generation (RAG) technique and large language models (LLM) to provide
        context-sensitive interactions. 🧠</h5>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Rob's Pages
    st.subheader("⬅️☜ Rob's Capabilities")
    st.write(
        """
- **Keywords-Research(beta)**: Search with Bing and chat about selected web pages via a history-aware [LCEL retrieval chain](https://docs.langchain.com/oss/python/langchain/retrieval)
- **Chat-file**: General Chat on data (PDF, TXT, CSV, XLSX) with a [FAISS vectorstore](https://github.com/facebookresearch/faiss) (indexes the most relevant parts to answer the user) | history-aware LCEL retrieval chain
- **Chat-web**: General Chat about a given website, stored in a [FAISS vectorstore](https://github.com/facebookresearch/faiss) | history-aware LCEL retrieval chain
- **Text-Similarity-score(beta)**: Cosine similarity of two texts using Ollama `nomic-embed-text` embeddings
"""
    )
    st.markdown("---")

    # Gallery thumbnails
    directory_path = "Gallery/"
    image_files = [
        file
        for file in os.listdir(directory_path)
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
    ]
    for image_file in image_files:
        image_path = os.path.join(directory_path, image_file)
        st.image(image_path)


# Native multipage navigation (replaces st-pages). The "download" page is
# intentionally omitted from the nav so it stays hidden, matching the old
# hide_pages(["download"]) behavior; it is still reachable from in-app links.
nav = st.navigation([
    st.Page(render_home, title="Home", icon="🏠", default=True),
    st.Page("pages/0_Keywords-Research-beta.py", title="Keywords-research", icon="💻"),
    st.Page("pages/1_Robby-Chat-file.py", title="Chat-file", icon="📄"),
    st.Page("pages/2_Robby-Chat-web.py", title="Chat-web", icon="🌐"),
    st.Page("pages/3_Text-Similarity-beta.py", title="Text-Similarity-score", icon="📚"),
])
nav.run()
