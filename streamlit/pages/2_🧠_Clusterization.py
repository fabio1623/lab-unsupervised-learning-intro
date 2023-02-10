import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import pickle

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
    
def clusterize_data(dataframe):
    with st.spinner('Clusterizing data...'):
        X = dataframe.drop(['_id', 'name', 'artists'], axis=1)
        y = dataframe['name']

        model = KMeans(n_clusters=9)
        min_max_scaler = MinMaxScaler().fit(X)
        X_normalized = min_max_scaler.transform(X)
        model.fit(X_normalized)

        kmeans_model_with_scaler = {
            "min_max_scaler": min_max_scaler,
            "model": model
        }

        clusters = model.predict(X_normalized)
        dataframe = pd.concat([dataframe,pd.Series(clusters, name='cluster')],axis=1)

        return dataframe, kmeans_model_with_scaler
    
def save_data_and_model(dataframe, kmeans_model_with_scaler):
    with st.spinner('Saving data into clusterized_data.csv...'):
        dataframe.to_csv("data/clusterized_data.csv", index=False)
    with st.spinner('Saving model and scaler into kmeans_model_with_scaler.pkl...'):
        with open("data/kmeans_model_with_scaler.pkl", "wb") as file:
            pickle.dump(kmeans_model_with_scaler, file)


st.write("# 🧠 Model Tester")



if "mongo_db_collection" not in st.session_state:
    st.session_state["mongo_db_collection"] = None


if st.session_state["mongo_db_collection"] is None:
    st.warning("Please, configure database connection in 'Database' section.")
else:
    if st.button("Clusterize data"):
        data = load_data(st.session_state["mongo_db_collection"])
        data, kmeans_model_with_scaler = clusterize_data(data)

        save_data_and_model(data, kmeans_model_with_scaler)

        st.dataframe(data[:10], use_container_width=True)