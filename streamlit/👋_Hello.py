import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Ready for some song recommendation?")

with st.container():
    image = Image.open('content/giphy.gif')
    st.image(image)