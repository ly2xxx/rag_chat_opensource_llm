import os
import pandas as pd
from bs4 import BeautifulSoup
import requests as r
import streamlit as st
from io import StringIO
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from datetime import datetime
from st_pages import hide_pages
import re

CONST_CHECKBOX_COLUMN = 'Select'

#To be able to update the changes made to modules in localhost (press r)
def reload_module(module_name):
    import importlib
    import sys
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]

def generate_filename(query_keywords, web_context):
    domain = query_keywords.replace(" ", "_").replace("+","_")

    # Format the current date
    current_date = datetime.now().strftime("%d%m%Y")

    # Content size
    content_size = len(web_context)
    
    # Concatenate the parts to create the filename
    filename = f"{domain}-{current_date}-{content_size}"
    
    return filename

def input_callback():
    st.session_state["reset_chat"] = True
    st.session_state["keysearch_ready"]=False

def dataframe_with_selections(df):
    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df,
        hide_index=False,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df[CONST_CHECKBOX_COLUMN]]

    return selected_rows.drop(CONST_CHECKBOX_COLUMN, axis=1)

@st.cache_data
def bing_search(query):
    # result_df=pd.Series([])
    try:
        if query.startswith("https://www.bing.com"):
            query_url = query
        else:
            query_url = f"https://www.bing.com/search?q={query}"
        req = r.get(query_url,
                    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"})
        result_str = '<html><table style="border: none;">' #Initializing the HTML code for displaying search results
        
        if req.status_code == 200: #Status code 200 indicates a successful request
            bs = BeautifulSoup(req.content, features="html.parser") #converting the content/text returned by request to a BeautifulSoup object
            search_result = bs.find_all("li", class_="b_algo") #'b_algo' is the class of the list object which represents a single result
            search_result = [str(i).replace("<strong>","") for i in search_result] #removing the <strong> tag
            search_result = [str(i).replace("</strong>","") for i in search_result] #removing the </strong> tag
            result_df = pd.DataFrame() #Initializing the data frame that stores the results
            pattern = r"q=([^&]+)" 
            match = re.search(pattern, query_url)
            if match:
                query_string = match.group(1)
            else:
                query_string = query
            
            for n,i in enumerate(search_result): #iterating through the search results
                individual_search_result = BeautifulSoup(i, features="html.parser") #converting individual search result into a BeautifulSoup object
                h2 = individual_search_result.find('h2') #Finding the title of the individual search result
                href = h2.find('a').get('href') #title's URL of the individual search result
                cite = f'{href[:50]}...' if len(href) >= 50 else href # cite with first 20 chars of the URL
                url_txt = h2.find('a').text #title's text of the individual search result
                #In a few cases few individual search results doesn't have a description. In such cases the description would be blank
                description = "" if individual_search_result.find('p') is None else individual_search_result.find('p').text
                #Appending the result data frame after processing each individual search result
                # result_df = result_df.append(pd.DataFrame({"Title": url_txt, "URL": href, "Description": description}, index=[n]))
                result_df = pd.concat([result_df, pd.DataFrame({CONST_CHECKBOX_COLUMN:False, "Title": url_txt, "URL": href, "Description": description}, index=[n])])
                count_str = f'<b style="font-size:20px;">Bing Search returned {len(result_df)} results</b>'
                ########################################################
                ######### HTML code to display search results ##########
                ########################################################
                result_str += f'<tr style="border: none;"><h3><a href="{href}" target="_blank">{url_txt}</a></h3></tr>'+\
                f'<tr style="border: none;"><strong style="color:green;">{cite}</strong></tr>'+\
                f'<tr style="border: none;">{description}</tr>'+\
                f'<tr style="border: none;"><td style="border: none;"></td></tr>'
            result_str += '</table></html>'

        #if the status code of the request isn't 200, then an error message is displayed along with an empty data frame        
        else:
            result_df = pd.DataFrame({"Title": "", "URL": "", "Description": ""}, index=[0])
            result_str = '<html></html>'
            count_str = '<b style="font-size:20px;">Looks like an error!!</b>'
            
    #if an exception is raised, then an error message is displayed along with an empty data frame
    except Exception as e:
        st.error(f"Error: {str(e)}")
        result_df = pd.DataFrame({"Title": "", "URL": "", "Description": ""}, index=[0])
        result_str = '<html></html>'
        count_str = '<b style="font-size:20px;">Looks like an error!!</b>'  

    st.markdown(f'{count_str}', unsafe_allow_html=True)
    st.markdown(f'{result_str}', unsafe_allow_html=True)
    st.markdown('<h3>Data Frame of the above search result</h3>', unsafe_allow_html=True)

    return result_df, query_string

hide_pages(["download"])
history_module = reload_module('modules.history')
layout_module = reload_module('modules.layout')
utils_module = reload_module('modules.utils')
sidebar_module = reload_module('modules.sidebar')

ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

# layout.show_header("Keywords")

user_api_key = utils.load_api_key()

# if not user_api_key:
#     layout.show_api_key_missing()
# else:
#     os.environ["OPENAI_API_KEY"] = user_api_key

query = st.text_input('(use "+" to connect keywords, to resolve UnboundLocalError copy the search string from Bing url):', placeholder="Enter Search keyword(s), for example: movie+review", help='Enter the search keywords and hit Enter/Return', on_change=input_callback)
query = query.replace(" ", "+") #replacing the spaces in query result with +

if len(query.strip())>0:
    print("query is called with keyword: " + query)
    query_result, query_str = bing_search(query)

    if not query_result.empty:
        selection = dataframe_with_selections(query_result)
        st.write("Your selection:")
        st.table(selection)
        st.session_state["keyword_selections"] = selection['URL'].to_list()
        print(st.session_state["keyword_selections"])
    else:
        st.write("No results found. Please try a different search query.")

    if st.button("Submit for chatbot research") or st.session_state["keysearch_ready"]:
        web_context = utils.handle_webloads(st.session_state["keyword_selections"])

        if web_context:

            # Configure the sidebar
            sidebar.show_options()
            sidebar.about()

            # Initialize chat history
            history = ChatHistory()
            try:
                uploaded_file = StringIO(web_context)

                web_context = web_context.strip()

                uploaded_file.name = generate_filename(query_str, web_context)+".txt"

                chatbot = utils.setup_chatbot(
                    uploaded_file, st.session_state["model"], st.session_state["temperature"]
                )

                st.session_state["keysearch_ready"] = utils.setup_conversation_cockpit(layout, sidebar, history, uploaded_file, chatbot)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.session_state["keysearch_ready"]=False