import streamlit as st
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
import base64
import shutil
from datetime import datetime
import os
import time

VECTOR_PATH = "embeddings"
DOWNLOAD_PATH = "downs/"

def create_download_zip(zip_directory, zip_path):
    """ 
        zip_directory (str): path to directory  you want to zip 
        zip_path (str): where you want to save zip file
        filename (str): download filename for user who download this
    """
    shutil.make_archive(DOWNLOAD_PATH + zip_path, 'zip', zip_directory)
    filename = DOWNLOAD_PATH + zip_path + ".zip"
    with open(filename, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/zip;base64,{b64}" download=\'{filename}\'>\
            vectors samples\
        </a>'
        st.markdown(href, unsafe_allow_html=True)

def delete_old_files(directory_path):
    # Get the current time
    current_time = time.time()

    # Calculate the timestamp for two days ago
    two_days_ago = current_time - 2 * 24 * 3600  # 2 days in seconds

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Check if the file is a regular file and its modification time is older than two days
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < two_days_ago:
            # Delete the file
            os.remove(file_path)
            print(f"Deleted: {file_path}")



st.set_page_config(layout="wide", page_icon="💬", page_title="Robby | dl🤖")

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

user_api_key = utils.load_api_key()

sidebar.about()

if True:
    current_datetime = datetime.now().strftime("pkl-%d%m%Y.%H.%M.%S")
    create_download_zip(VECTOR_PATH, current_datetime)
    delete_old_files(VECTOR_PATH)
    delete_old_files(DOWNLOAD_PATH)