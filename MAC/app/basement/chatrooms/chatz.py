import streamlit as st
from streamlit import session_state
from datetime import datetime
import random

from funcs import closeSession, openSession
from local_services.local_db import Sessions


def chatz(userAccount):
  if session_state['currentSession'] != None:
    if session_state['currentSession']['tab'] != 'Chatz!':
      closeSession()

  st.header('The Actual Chatrooms')

  chatz_selected = st.radio(
    'What you want to do',
    options=['Join Chatroom', 'Make Chatroom', 'View Public Chatrooms', '---']
  )
  st.write('---')

  if chatz_selected == 'Join Chatroom':
    joinchatroom = st.form('join_chatroom')
    with joinchatroom:
      st.header('Join Chatroom')
      id = st.text_input('Enter Id')

      press = st.form_submit_button('Join')
      if press:
        session = Sessions.find_one({'_id': id})
        if id == 'OMEGA_CHAT' or session == None or session.get('isRandom'):
          st.error('Invalid Id')
        else:
          session_state['currentSession'] = {
            '_id': id,
            'origLength': len(session['history']),
            'idle': False,
            'tab': 'Chatz!',
            'isRandom': False
          }

  elif chatz_selected == 'Make Chatroom':
    makechatroom = st.form('make_chatroom')
    with makechatroom:
      st.header('Create Chatroom')
      title = st.text_input('Enter Title')
      description = st.text_input('Enter Description')
      private = st.radio(
        'Private or Public?',
        options=['private', 'public']
      )
      press = st.form_submit_button('Create')
      if press:
        if len(title) > 25:
          st.error('Title too long')
        elif len(description) > 250:
          st.error('Description too long')
        elif title.strip() == '':
          st.error('Enter a title')
        else:
          while True:
            code = ''
            for i in range(5):
              code += str(random.randint(0,9))
            if code not in [session['_id'] for session in Sessions.find()]:
              break

          session = {
            '_id': code,
            'title': title,
            'description': description,
            'isRandom': False,
            'privacy': private,
            'people': [],
            'history': [],
            'date': datetime.utcnow().isoformat(),
            'idle': None
          }

          Sessions.insert_one(session)
          session_state['currentSession'] = {
            '_id': code,
            'origLength': 0,
            'idle': False,
            'tab': 'Chatz!',
            'isRandom': False
          }
          st.rerun()

  elif chatz_selected == 'View Public Chatrooms':
    sessions = [
      session for session in Sessions.find()
      if session['_id'] != 'OMEGA_CHAT'
      and session.get('privacy') == 'public'
      and session.get('isRandom') == False
    ]

    if len(sessions) == 0:
      st.error('No Public Chatrooms right now')
    else:
      if len(sessions) == 1:
        i = 1
      else:
        i = st.slider('Enter Index', min_value=1, max_value=len(sessions), value=1)

      session = sessions[i-1]

      st.header(session['title'])
      st.subheader(session['description'])
      st.write('Current Active People: '+', '.join([person['username'] for person in session['people']]))
      st.subheader('Id: '+session['_id'])

      press = st.button('Reload')
      if press:
        st.rerun()

  st.write('---')

  if session_state['currentSession'] != None and chatz_selected != 'View Public Chatrooms':
    response = openSession(session_state['currentSession']['_id'], 'Chatz!')
    if response == False:
      st.error('Session Deleted')
      session_state['currentSession'] = None
    elif response == 'spam':
      st.rerun()
