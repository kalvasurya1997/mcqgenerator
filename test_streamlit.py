import streamlit as st

st.title("🚀 Streamlit Debug Test")
st.write("If you see this, Streamlit is working!")

uploaded_file = st.file_uploader("Upload a file")
if uploaded_file:
    st.write("File Uploaded Successfully!")
