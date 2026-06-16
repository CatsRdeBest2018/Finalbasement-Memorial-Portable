import streamlit as st
from datetime import datetime
import time

from local_services.local_db import Suggestions


def normalize_id(value):
  if isinstance(value, dict) and '$oid' in value:
    return str(value['$oid'])
  return str(value)


def suggestions(userAccount):
  st.header('Make a suggestion')
  st.write('for da basement')
  st.write('---')

  targetDate = datetime(2024, 2, 1, 1, 1, 1)

  if datetime.utcnow() < targetDate:
    st.error('Wait untill feb 1st cuz i dont feel like doing anything rn')
  else:
    n = 0

    for suggestion in Suggestions.find():
      if normalize_id(suggestion['userid']) == normalize_id(userAccount['_id']):
        n += 1

    if n == 3:
      st.error('Only three suggestions at a time pluh')
    else:
      suggestionform = st.form('suggestion-form')

      with suggestionform:
        st.header('Suggestion')
        suggestion = st.text_input(label='Text')
        anonymous = st.checkbox(label='Be anonymous?')
        press = st.form_submit_button(label='Submit')

        if press:
          if suggestion.strip() == '':
            st.error('Enter a suggestion')
          else:
            Suggestions.insert_one({
              'userid': userAccount['_id'],
              'content': suggestion,
              'anonymous': anonymous,
              'date': datetime.utcnow().isoformat()
            })

            st.success('Thx!')
            time.sleep(3)
            st.rerun()
