import streamlit as st
import pandas as pd
import pickle

def find_matches(dataframe, song_title):
    with st.spinner("Searching matches..."):
        matches = dataframe[(dataframe['name'].notna()) & (dataframe['name'].str.contains(song_title, case=False))]
        if matches.empty:
            return None
        else:
            return matches
        
def get_recommendation(dataframe, matches, song_id):
    with st.spinner("Searching recommendation..."):
        cluster = matches[matches['_id'] == song_id]['cluster'].values[0]
        random_song = dataframe[(dataframe['cluster'] == cluster) & ~(dataframe['_id'] == song_id) & ~(dataframe['name'] == song_id)].sample()
        if random_song.empty:
            return None
        else:
            return random_song

def load_data():
    with st.spinner("Loading data..."):
        try:
            st.session_state["clusterized_data"] = pd.read_csv("data/clusterized_data.csv")
        except:
            pass

def load_model_with_scaler():
    with st.spinner("Loading model and scaler..."):
        try:
            with open(f'data/kmeans_model_with_scaler.pkl', "rb") as file:
                st.session_state["kmeans_model_with_scaler"] = pickle.load(file)
        except:
            pass

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


def ask_title():
    st.write("# Provide the title of a song you like")

    st.session_state["title"] = st.text_input("Title")

    if st.button("Search"):
        matches = find_matches(st.session_state["clusterized_data"], st.session_state["title"])
        if matches is None:
            st.warning("No matching song found. Try another one.")
        else:
            st.session_state["matches"] = matches
            st.experimental_rerun()

def ask_id():
    st.write("# Type _id of corresponding song")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state["id"] = st.text_input("ID")

        if st.button("Submit"):
            recommended_song = get_recommendation(st.session_state["clusterized_data"], st.session_state["matches"], st.session_state["id"])
            if recommended_song is None:
                st.warning("No recommendation found.")
            else:
                st.session_state["recommended_song"] = recommended_song
                st.experimental_rerun()

        if st.button("Back to title selection"):
            st.session_state["title"] = None
            st.session_state["matches"] = None
            st.experimental_rerun()

    with col2:
        display_matches()

def display_matches():
    nb_matches = st.session_state["matches"].shape[0]
    title = st.session_state["title"]
    st.write(f"### {nb_matches} matches for '{title}'")
    st.dataframe(st.session_state["matches"][['_id', 'name', 'artists']], use_container_width=True)

def display_recommendation():
    st.dataframe(st.session_state["recommended_song"], use_container_width=True)

    if st.button("Back to id selection"):
        st.session_state["id"] = None
        st.session_state["recommended_song"] = None
        st.experimental_rerun()


st.set_page_config(
    page_title="Recommender",
    page_icon="",
)

init()

if st.session_state["clusterized_data"] is None or st.session_state["kmeans_model_with_scaler"] is None:
    load_data()
    load_model_with_scaler()

if st.session_state["clusterized_data"] is None or st.session_state["kmeans_model_with_scaler"] is None:
    st.error("clusterized_data.csv / kmeans_model_with_scaler.pkl could not be found. Please, run clusterize data in 'Clusterization' section.")
    st.stop()

if st.session_state["matches"] is None:
    ask_title()
elif st.session_state["id"] is None:
    ask_id()
else:
    display_recommendation()