import streamlit as st

def init():
    if "clusterized_data" not in st.session_state:
        st.session_state["clusterized_data"] = None

    if "kmeans_model_with_scaler" not in st.session_state:
        st.session_state["kmeans_model_with_scaler"] = None

    if "title" not in st.session_state:
        st.session_state["title"] = None

    if "matches" not in st.session_state:
        st.session_state["matches"] = None

    if "id" not in st.session_state:
        st.session_state["id"] = None

    if "recommended_song" not in st.session_state:
        st.session_state["recommended_song"] = None