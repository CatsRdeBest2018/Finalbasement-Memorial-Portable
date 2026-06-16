import streamlit as st
from streamlit import session_state
from funcs import closeSession, openSession


def omega_chat():
  if session_state['currentSession'] != None:
    if session_state['currentSession']['tab'] != 'Omega Chat!':
      closeSession()
  response = openSession('OMEGA_CHAT', 'Omega Chat!')
  if response == 'spam':
    st.warning("Your session has been closed due to spamming. Please wait a moment before trying again.")
    st.rerun()
