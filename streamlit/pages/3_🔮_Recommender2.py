import streamlit as st
import pickle
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data_and_model(model_file, data_file):
    with open(model_file, 'rb') as file:
        model = pickle.load(file)

    data = pd.read_csv(data_file)
    return model, data

def get_random_row(data, selected_row, cluster_col='cluster'):
    same_cluster = data[data[cluster_col] == selected_row[cluster_col]]
    return same_cluster[same_cluster.index != selected_row.name].sample()

def display_radar_chart(data, selected_row1, selected_row2):
    fig = px.line_polar(data.loc[[selected_row1, selected_row2]], r=data.columns, theta=data.columns, line_close=True)
    st.write(fig)


model, data = load_data_and_model('data/kmeans_model_with_scaler.pkl', 'data/clusterized_data.csv')
title = st.text_input('Enter title:')
if title:
    matching_results = data[(data['name'].notna()) & (data['name'].str.contains(title, case=False))]
    if not matching_results.empty:
        page = st.sidebar.slider("Page", 1, round(matching_results.shape[0] / 10), 1)
        selected_row = st.selectbox(
            'Select a row:',
            matching_results.iloc[(page - 1) * 10: page * 10].index
        )
        st.dataframe(matching_results.iloc[(page - 1) * 10: page * 10])
        selected_row1 = data.loc[selected_row]
        selected_row2 = get_random_row(data, selected_row1)
        st.dataframe(selected_row1.to_frame().T)
        st.dataframe(selected_row2)
        display_radar_chart(data, selected_row1.name, selected_row2.index[0])
        if st.button('Back'):
            st.write(' ')
    else:
        st.write('No matching results found.')