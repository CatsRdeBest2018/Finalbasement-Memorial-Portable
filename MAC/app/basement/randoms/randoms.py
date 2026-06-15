import streamlit as st
from streamlit import session_state
from streamlit_extras.stateful_button import button
import random
import time
from datetime import datetime

from funcs import closeSession, openSession
from local_services.local_db import Sessions, Randoms
from local_services.local_storage import get_local_file_url


def normalize_id(value):
  if isinstance(value, dict) and '$oid' in value:
    return str(value['$oid'])
  return str(value)


def randoms(userAccount):
  if session_state['currentSession'] != None:
    if session_state['currentSession']['isRandom'] == False:
      closeSession()

  st.header('Randoms')
  st.write('talk to random people also doing randoms')
  st.write('---')

  begin = button(label='Begin', key='begin-randoms')

  if begin:
    st.write('---')
    st.subheader('Connecting...')

    if session_state['currentSession'] == None:
      random_queue = list(Randoms.find())

      if len(random_queue) == 0:
        while True:
          code = ''
          for i in range(5):
            code += str(random.randint(0,9))
          if code not in [session['_id'] for session in Sessions.find()]:
            break

        session = {
          '_id': code,
          'title': 'Random Chatroom',
          'description': 'Random people will come and go',
          'isRandom': True,
          'privacy': 'private',
          'people': [],
          'history': [],
          'date': datetime.utcnow().isoformat(),
          'idle': None
        }

        Sessions.insert_one(session)

        Randoms.insert_one({
          '_id': userAccount['_id'],
          'sessionId': code,
          'taken': None,
          'date': datetime.utcnow().isoformat()
        })

        openSession(code, 'Randoms')
        st.rerun()

      else:
        que = list(Randoms.find())

        if que == None or len(que) == 0:
          st.rerun()

        other = que[0]

        try:
          Randoms.update_one(
            {'_id': other['_id']},
            {'$set': {'taken': userAccount['_id']}}
          )
        except Exception:
          st.rerun()

        time.sleep(1.5)

        que = list(Randoms.find())

        if que == None or len(que) == 0:
          st.rerun()

        other = que[0]

        if normalize_id(other.get('taken')) != normalize_id(userAccount['_id']):
          st.rerun()

        try:
          Randoms.delete_one({'_id': other['_id']})
        except Exception:
          st.rerun()

        session = Sessions.find_one({'_id': other['sessionId']})

        if session == None:
          st.error('Random session was deleted')
          st.rerun()

        while True:
          code = ''
          for i in range(5):
            code += str(random.randint(0,9))
          if code not in [i['_id'] for i in session['history']]:
            break

        Sessions.update_one(
          {'_id': other['sessionId']},
          {
            '$push': {
              'history': {
                '_id': code,
                'text': 'Random Joined the Chat!',
                'userid': None,
                'username': 'Server',
                'path': get_local_file_url('profile-images/guest.png'),
                'date': datetime.utcnow().isoformat()
              }
            }
          }
        )

        openSession(other['sessionId'], 'Randoms')
        st.rerun()

    else:
      continueButton = st.button(label='Continue')

      if continueButton:
        closeSession()
        st.header('Continuing...')
        st.rerun()

      response = openSession(session_state['currentSession']['_id'], 'Randoms')

      if response == False:
        st.error('Session Deleted')
        session_state['currentSession'] = None
      elif response == 'spam':
        st.rerun()
