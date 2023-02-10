import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering, AffinityPropagation
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import davies_bouldin_score

st.set_page_config(
    page_title="Model Generator",
    page_icon="🧠",
)

def clean_data(dataframe):
    columns_to_drop = ['audio_features.type', 'audio_features.id', 'audio_features.uri', 'audio_features.track_href', 'audio_features.analysis_url']
    dataframe.drop(columns=columns_to_drop, axis=1, inplace=True)
    dataframe['name'] = dataframe['name'].str.lower()
    dataframe['artists'] = [', '.join([artist['name'].lower() for artist in x]) for x in dataframe['artists']]
    return dataframe.dropna(axis=0)

def load_data(mongo_db_collection):
    with st.spinner('Loading data...'):
        cursor = mongo_db_collection.find({"audio_features": {"$ne": None} }, {'_id': 1, 'name': 1, 'artists': 1, 'audio_features': 1})
        data = pd.json_normalize(cursor)
    with st.spinner('Cleaning data...'):
        data = clean_data(data)
        data = data.sample(frac=1)
        return data

st.write("# 🧠 Model Tester")

if "full_data" not in st.session_state:
    st.session_state["full_data"] = None

if "mongo_db_collection" not in st.session_state:
    st.session_state["mongo_db_collection"] = None

if "kmeans_model_with_scaler" not in st.session_state:
    st.session_state["kmeans_model_with_scaler"] = None

if st.session_state["full_data"] is None:
    if st.session_state["mongo_db_collection"] is None:
        st.warning("Please, configure database connection in 'Database' section.")
    else:
        if st.button("Load data"):
            st.session_state["full_data"] = load_data(st.session_state["mongo_db_collection"])
            st.info("Database loaded.")
            st.experimental_rerun()
else:
    if st.button("Unload database"):
        st.session_state["full_data"] = None
        st.experimental_rerun()

    X = st.session_state["full_data"].drop(['_id', 'name', 'artists'], axis=1)
    y = st.session_state["full_data"]['name']

    if st.button("Clusterize data"):
        with st.spinner('Clustering data...'):
            model = KMeans(n_clusters=9)
            min_max_scaler = MinMaxScaler().fit(X)
            X_normalized = min_max_scaler.transform(X)
            model.fit(X_normalized)

            st.session_state["kmeans_model_with_scaler"] = {
                "min_max_scaler": min_max_scaler,
                "model": model
            }

            clusters = model.predict(X_normalized)
            st.session_state["full_data"] = pd.concat([st.session_state["full_data"],pd.Series(clusters, name='cluster')],axis=1)
            st.dataframe(st.session_state["full_data"][:10], use_container_width=True)