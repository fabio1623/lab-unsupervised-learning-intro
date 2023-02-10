import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Ready for some song recommendation?")

image = Image.open('content/hotpot.png')
st.image(image, use_column_width='always')