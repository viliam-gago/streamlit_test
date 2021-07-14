import streamlit as st
import time

@st.cache(suppress_st_warning=True)
def expensive_computation(a, b):
    st.write("aaa")
    time.sleep(2)  # 👈 This makes the function take 2s to run
    return a * b

a = 2
b = 210
res = expensive_computation(a, b)

st.write("Result:", res)
