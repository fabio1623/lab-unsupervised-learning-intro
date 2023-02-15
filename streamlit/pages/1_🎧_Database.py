import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Database", 
    page_icon="🎧")


def get_mongo_db_collection(username, password):
    mongo_db_collection = None
    nb_documents = None
    error = None

    with st.spinner('Verify connection...'):
        try:
            mongo_db_client = MongoClient(f'mongodb://{username}:{password}@localhost:27018')
            db = mongo_db_client['spotify-db']
            mongo_db_collection = db['song-collection']
            nb_documents = mongo_db_collection.count_documents({})
        except Exception as exception:
            error = f"Could not connect to database: {exception}"

        return {
            'mongo_db_collection': mongo_db_collection,
            'nb_documents': nb_documents,
            'error': error
        }
    
def clean_data(dataframe):
    columns_to_drop = ['audio_features.type', 'audio_features.id', 'audio_features.uri', 'audio_features.analysis_url']
    dataframe.drop(columns=columns_to_drop, axis=1, inplace=True)
    dataframe['artists'] = [', '.join([artist['name'] for artist in x]) for x in dataframe['artists']]
    return dataframe.dropna(axis=0)
    
def load_data(mongo_db_collection, chunk_size, page):
    with st.spinner('Loading data...'):
        cursor = mongo_db_collection.find({"audio_features": {"$ne": None} }, {'_id': 1, 'name': 1, 'artists': 1, 'audio_features': 1})
        data = pd.json_normalize(cursor[(page-1)*chunk_size:page*chunk_size])
        data = clean_data(data)
        return data
    
def display_heatmap(dataframe):
    with st.spinner('Loading...'):
            corr=dataframe.corr()

            mask=np.triu(np.ones_like(corr, dtype=bool))     # generate a mask for the upper triangle

            f, ax=plt.subplots(figsize=(11, 9))                 # set up the matplotlib figure

            cmap=sns.diverging_palette(220, 10, as_cmap=True)   # generate a custom diverging colormap

            sns.heatmap(corr, mask=mask, cmap=cmap,             # draw the heatmap with the mask and correct aspect ratio
                        vmax=.3, center=0, square=True,
                        linewidths=.5, cbar_kws={"shrink": .5})
            st.write(f)

def set_connection_variables(mongo_db_collection, nb_documents):
    st.session_state["mongo_db_collection"] = mongo_db_collection
    st.session_state["nb_documents"] = nb_documents
    st.session_state["data"] = None

if "mongo_db_collection" not in st.session_state or 'nb_documents' not in st.session_state:
    set_connection_variables(None, None)

if "data" not in st.session_state:
    st.session_state["data"] = None
    

if st.session_state["mongo_db_collection"] is None:
    st.write("# 🎧 Provide Database Credentials")
    with st.form("verify-connection-form"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")

        if st.form_submit_button("Submit"):
            response = get_mongo_db_collection(username, password)
            if response['error'] != None:
                st.error('Please provide valid credentials.')
            else:
                set_connection_variables(response['mongo_db_collection'], response['nb_documents'])
                st.experimental_rerun()
else:
    if st.button("Reset Connection"):
        set_connection_variables(None, None)
        st.experimental_rerun()
    
    st.write("# 🎧 Data Visualization")
    with st.form("load-data-form"):
        chunk_size = st.number_input("Number of documents to display", value=5, step=5, min_value=5, max_value=st.session_state["nb_documents"], key="chunck_size")
        max_pages = round(st.session_state["nb_documents"]/chunk_size)
        page = st.number_input("Page to display", value=1, step=1, min_value=1, max_value=max_pages, key="page")

        if st.form_submit_button("Load data"):
            st.session_state["data"] = load_data(st.session_state["mongo_db_collection"], chunk_size, page)


    if st.session_state["data"] is not None:
        tab1, tab2 = st.tabs(["General", "Details"])

        with tab1:
            st.write(st.session_state["data"])
        with tab2:
            if st.checkbox("Show summary statistics", key="show_stats_checkbox"):
                st.write(st.session_state["data"].describe())
            if st.checkbox("Show column names", key="show_cols_checkbox"):
                st.write(st.session_state["data"].columns)
            if st.checkbox("Show data types", key="show_data_type_checkbox"):
                st.write(st.session_state["data"].dtypes)
            if st.checkbox("Show heatmap", key="show_heatmap_checkbox"):
                display_heatmap(st.session_state["data"])