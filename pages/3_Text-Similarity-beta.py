import streamlit as st
from modules.similarity import SimilarityScorer
from st_pages import hide_pages

hide_pages(["download"])
st.title("Text Similarity Calculator")

text1 = st.text_area("Enter first text:", "")
text2 = st.text_area("Enter second text:", "")

scorer = SimilarityScorer() 
    
if st.button("Score"):
    score = scorer.score(text1, text2)
    st.write("Similarity score:", score)