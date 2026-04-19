import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Recruitment Dashboard")

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_data():
    return conn.read(
        spreadsheet="1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc"
    )

df = load_data()

st.dataframe(df)
st.metric("Total Candidate", len(df))
