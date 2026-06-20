import streamlit as st
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
import shutil
from datetime import datetime
import os
import time

VECTOR_PATH = "embeddings"
DOWNLOAD_PATH = "downs/"


def create_download_button(zip_directory, zip_name):
    """Zip a directory of FAISS index folders and offer it for download."""
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    archive_base = os.path.join(DOWNLOAD_PATH, zip_name)
    zip_path = shutil.make_archive(archive_base, 'zip', zip_directory)
    with open(zip_path, 'rb') as f:
        st.download_button(
            label="Download vectors samples (.zip)",
            data=f.read(),
            file_name=f"{zip_name}.zip",
            mime="application/zip",
        )


def delete_old_files(directory_path):
    """Delete files and index folders older than two days."""
    if not os.path.isdir(directory_path):
        return
    two_days_ago = time.time() - 2 * 24 * 3600  # 2 days in seconds

    for name in os.listdir(directory_path):
        path = os.path.join(directory_path, name)
        if os.path.getmtime(path) >= two_days_ago:
            continue
        if os.path.isfile(path):
            os.remove(path)
            print(f"Deleted: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            print(f"Deleted dir: {path}")


# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

sidebar.about()

current_datetime = datetime.now().strftime("vectors-%d%m%Y.%H.%M.%S")
create_download_button(VECTOR_PATH, current_datetime)
delete_old_files(VECTOR_PATH)
delete_old_files(DOWNLOAD_PATH)
