import streamlit as st

class Layout:

    def show_header(self, types_files):
        """
        Displays the header of the app
        """
        st.markdown(
            f"""
            <h1 style='text-align: center;'> Ask Rob about your {types_files} </h1>
            """,
            unsafe_allow_html=True,
        )
