import streamlit as st

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


st.set_page_config(
    page_title="Recommender",
    page_icon="",
)

st.write("# Recommender")

if "full_data" not in st.session_state:
    st.session_state["full_data"] = None

if "kmeans_model_with_scaler" not in st.session_state:
    st.session_state["kmeans_model_with_scaler"] = None

if "matches" not in st.session_state:
    st.session_state["matches"] = None

if st.session_state["full_data"] is None or st.session_state["kmeans_model_with_scaler"] is None:
    st.warning("Please, clusterize data in 'Clusterization' section.")
elif st.session_state["matches"] is None:
    with st.form("song-title-form"):
        song_title = st.text_input("Provide the title of a song you like")

        if st.form_submit_button("Search"):
            matches = find_matches(st.session_state["full_data"], song_title)
            if matches is None:
                st.warning("No matching song found. Try another one.")
            else:
                st.session_state["matches"] = matches
                st.experimental_rerun()
else:
    with st.form("song-id-form"):
        if st.form_submit_button("Back"):
            st.session_state["matches"] = None
            st.experimental_rerun()
            
        song_id = st.text_input("Provide the id of the matching song")
        recommended_song = None
        if st.form_submit_button("Get recommendation"):
            recommended_song = get_recommendation(st.session_state["full_data"], st.session_state["matches"], song_id)
            if recommended_song is None:
                st.warning("No recommendation found.")
            else:
                st.write("Recommended song")
                st.dataframe(recommended_song[['_id', 'name', 'artists']], use_container_width=True)
    
    if recommended_song is None:
        st.dataframe(st.session_state["matches"][['_id', 'name', 'artists']], use_container_width=True)