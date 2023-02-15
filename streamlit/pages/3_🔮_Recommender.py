import streamlit as st
import pandas as pd
from millify import millify, prettify
import plotly.graph_objects as go

@st.cache_data
def load_data():
    try:
        return pd.read_csv("data/clusterized_data.csv")
    except:
        return None

@st.cache_data
def find_matches(data, title, artists):
    matches = data
    if title != '':
        matches = matches[(matches['name'].notna()) & (matches['name'].str.contains(title, case=False))]
    if artists != '':
        matches = matches[(matches['artists'].notna()) & (matches['artists'].str.contains(artists, case=False))]
    
    return matches

def get_recommended_song(data, index):
    selected_row = data.loc[index]
    same_cluster = data[data['cluster'] == selected_row['cluster']]
    return same_cluster[same_cluster.index != selected_row.name].sample()

def plot_scatter_polar(selected_match, recommendation, columns_to_display):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=selected_match[columns_to_display],
        theta=columns_to_display,
        fill='toself',
        name="Your Song",
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatterpolar(
        r=recommendation[columns_to_display],
        theta=columns_to_display,
        fill='toself',
        name="Recommended Song",
        line=dict(color='red')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        showlegend=True
    )

    return fig

def display_matches(matches, title, artists):
    nb_matches = matches.shape[0]
    st.subheader(f"{prettify(nb_matches, ',')} matches for '{title}' and '{artists}'")
    st.dataframe(matches[['name', 'artists']], use_container_width=True)

def display_feature_plot(data, matches, selected_index):
    selected_match = matches.loc[selected_index]
    st.subheader("Your Song")

    st.markdown(f"###### :headphones: : [{selected_match['name']}](https://open.spotify.com/track/{selected_match['_id']})")
    st.markdown(f"###### :speaking_head_in_silhouette: : {selected_match['artists']}")

    columns_to_display = [col for col in matches.columns if col not in ['_id', 'artists', 'name', 'cluster', 'audio_features.duration_ms', 'audio_features.tempo']]

    recommendation = get_recommended_song(data, selected_index).iloc[0]
    st.subheader("Recommended Song")
    st.markdown(f"###### :headphones: : [{recommendation['name']}](https://open.spotify.com/track/{recommendation['_id']})")
    st.markdown(f"###### :speaking_head_in_silhouette: : {recommendation['artists']}")

    plot = plot_scatter_polar(selected_match, recommendation,  columns_to_display)
    st.plotly_chart(plot, use_container_width=True)


st.title("🔮 Song Recommender")

data = load_data()
if data is None:
    st.error("Please, clusterize data through Clusterization section")
    st.stop()

nb_songs = data.shape[0]

st.success(f'Filter out data through Sidebar. [{millify(nb_songs, precision=1)} songs available]', icon="👈")

st.sidebar.header("Filters")
title = st.sidebar.text_input("Title", key="title")
artists = st.sidebar.text_input("Artists", key="artists")

if title == '' and artists == '':
    st.stop()

matches = find_matches(data, title, artists)

if matches.shape[0] > 1:
    indexes = ['']
    indexes += [prettify(index, ',') for index in matches.index]

    st.sidebar.header("Select Matching ID")
    selected_index = st.sidebar.selectbox(
            'ID',
            indexes,
            key="selected_index"
        )
else:
    selected_index = prettify(matches.index[0], ',')

col1, col2 = st.columns(2)

with col1:
    display_matches(matches, title, artists)

if selected_index == '':
    st.stop()

with col2:
    if st.button("Recommend something different"):
        display_feature_plot(data, matches, int(selected_index.replace(',', '')))
    else:
        display_feature_plot(data, matches, int(selected_index.replace(',', '')))