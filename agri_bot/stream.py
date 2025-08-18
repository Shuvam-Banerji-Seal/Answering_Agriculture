import streamlit as st

# Ask user to choose mode at the start
if "mode" not in st.session_state:
    st.session_state.mode = None

mode = st.radio(
    "How would you like to use the bot?",
    ["Free Model", "API-based Model"],
    index=None,  # 👈 this makes it start with nothing selected
)

if mode:
    st.session_state.mode = mode
    st.success(f"You selected: **{st.session_state.mode}**")
    # Proceed with your chatbot logic...
    if st.session_state.mode == "Free Model":
        st.write("Loading Free Model...")
        # load_model()
    else:
        st.write("Loading API-based Model...")
        # ai_bharat_load()
    st.stop()s