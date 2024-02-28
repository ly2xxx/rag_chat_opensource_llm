import streamlit as st
from st_pages import hide_pages, show_pages_from_config, add_page_title, show_pages, Page, Section
from PIL import Image
import os

# if not hasattr(st, 'already_started_server'):
#     # Hack the fact that Python modules (like st) only load once to
#     # keep track of whether this file already ran.
#     st.already_started_server = True

#     st.write('''
#         The first time this script executes it will run forever because it's
#         running a Flask server.

#         Just close this browser tab and open a new one to see your Streamlit
#         app.
#     ''')

#     from flask import Flask

#     app = Flask(__name__)

#     @app.route('/foo')
#     def serve_foo():
#         return 'This page is served via Flask!'

#     app.run(port=8888)

add_page_title()
show_pages_from_config()

show_pages(
    [
        Page("./streamlit_app.py", "Home", "🏠"),
        # Can use :<icon-name>: or the actual icon
        Page("./pages/0_Keywords-Research-beta.py", "Keywords-research", "💻"),
        Page("./pages/1_Robby-Chat-file.py", "Chat-file", "📄"),
        Page("./pages/2_Robby-Chat-web.py", "Chat-web", "🌐"),
        Page("./pages/download.py", "download", "⤓"),
    ]
)

hide_pages(["download"])

#Contact
with st.sidebar.expander("📬 Contact"):

#     st.write("**GitHub:**",
# "[ly2xxx/rag_chat_poc-tbc](https://github.com/ly2xxx/rag_chat_poc)")

    st.write("**Mail** : yang.li@barclays.com, rad.ricka@barclays.com")
    st.write("**Created by Yang, hosted by Rad**")


#Title
st.markdown(
    """
    <h2 style='text-align: center;'>Rob, your data-aware research assistant 🤖</h1>
    """,
    unsafe_allow_html=True,)

st.markdown("---")

def generate_thumbnail(image_path, thumbnail_size=(500, 500)):
    original_image = Image.open(image_path)
    thumbnail = original_image.resize(thumbnail_size)
    return thumbnail

mascot_image_file = "Gallery/mascot/01_mascot.jpeg"
thumbnail = generate_thumbnail(mascot_image_file)
st.image(thumbnail, caption="Rob", use_column_width=True)

#Description
typing_script = """
<style>
    #typed-text {
        overflow: hidden;
        white-space: nowrap; /* Set to nowrap to prevent line breaks */
        border-right: .15em solid orange;
        font-size: 13px; /* Adjust font size as needed */
        margin: 0 auto;
        letter-spacing: .15em;
        animation: typing 6s steps(100, end), blink-caret .5s step-end infinite; /* Adjust timing and steps */
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
    // Function to remove animation after completion
    function removeAnimation() {
        document.getElementById("typed-text").style.animation = "none";
    }

    // Call the removeAnimation function after the animation completes
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
    unsafe_allow_html=True)
st.markdown("---")


#Robby's Pages
st.subheader("⬅️☜ Rob's Capabilities")
st.write("""
- **Keywords-Research(beta)**: Search with Bing and chat about selected web pages [ConversationalRetrievalChain](https://python.langchain.com/en/latest/modules/chains/index_examples/chat_vector_db.html)
- **Chat-file**: General Chat on data (PDF, TXT,CSV) with a [vectorstore](https://github.com/facebookresearch/faiss) (index useful parts(max 4) for respond to the user) | works with [ConversationalRetrievalChain](https://python.langchain.com/en/latest/modules/chains/index_examples/chat_vector_db.html)
- **Chat-web**: General Chat about given website with [langchain-Sitemaploader](https://python.langchain.com/docs/integrations/document_loaders/sitemap) stored in a [vectorstore](https://github.com/facebookresearch/faiss) (index useful parts(max 4) for respond to the user) | works with [ConversationalRetrievalChain](https://python.langchain.com/en/latest/modules/chains/index_examples/chat_vector_db.html)
""")

st.markdown("---")

st.markdown("---")

# Specify the directory path containing image files
directory_path = "Gallery/"

# Get a list of image files in the directory
image_files = [file for file in os.listdir(directory_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

# Display thumbnails
for image_file in image_files:
    image_path = os.path.join(directory_path, image_file)
    st.image(image_path)
    
# hide_img_fs = '''
# <style>
# button[title="View fullscreen"]{
#     visibility: hidden;}
# </style>
# '''

# st.markdown(hide_img_fs, unsafe_allow_html=True)
    # thumbnail = generate_thumbnail(image_path)

    # st.image(thumbnail, caption=image_file, use_column_width=True)


# - **Robby-Sheet** (beta): Chat on tabular data (CSV) | for precise information | process the whole file | works with [CSV_Agent](https://python.langchain.com/en/latest/modules/agents/toolkits/examples/csv.html) + [PandasAI](https://github.com/gventuri/pandas-ai) for data manipulation and graph creation
# - **Robby-Youtube**: Summarize YouTube videos with [summarize-chain](https://python.langchain.com/en/latest/modules/chains/index_examples/summarize.html)

# #Contributing
# st.markdown("### 🎯 Contributing")
# st.markdown("""
# **Robby is under regular development. Feel free to contribute and help me make it even more data-aware!**
# """, unsafe_allow_html=True)





