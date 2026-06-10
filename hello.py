import streamlit as st

st.set_page_config(page_title="Hello", page_icon="👋")

st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ### Hi there! 👋

    Welcome to your first Streamlit app. This is a simple demo showing how to use Streamlit.

    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    """
)

st.write("---")

name = st.text_input("What's your name?", "World")
st.write(f"Hello, {name}! 🎉")

if st.button("Click me!"):
    st.write("✨ Button clicked! ✨")
