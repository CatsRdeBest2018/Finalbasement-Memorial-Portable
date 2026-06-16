import streamlit as st
from streamlit import session_state
from datetime import datetime
from funcs import convertTime
from local_services.local_db import Accounts, Archives


def normalize_datetime(value):
  if isinstance(value, datetime):
    return value

  if isinstance(value, dict) and '$date' in value:
    value = value['$date']

  if isinstance(value, str):
    cleaned = value.replace('Z', '+00:00')
    try:
      return datetime.fromisoformat(cleaned).replace(tzinfo=None)
    except ValueError:
      pass

  return datetime.utcnow()


def inbox(userAccount):
  st.header('Inbox')
  st.write('anything important will show up here')
  st.write('---')
  amount = len(userAccount['inbox'])
  if amount == 0:
    st.error('No messages')
  else:
    st.success('You have '+str(amount)+' Message(s)')
    clear = st.button('Clear Messages')
    if clear:
      if userAccount['inbox'] != []:
        archiveInbox = {'userid': userAccount['_id'], 'inbox': userAccount['inbox'], 'archiveType': 'clearedInbox', 'archiveDate': datetime.utcnow()}
        Archives.insert_one(archiveInbox)
      Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'inbox': []}})
      st.rerun()
    inbox = userAccount['inbox']
    inbox.reverse()
    for message in userAccount['inbox']:
      type = message['type']
      msg = message['msg']

      utc_offset = session_state['utcOffset']

      message_time = normalize_datetime(message['time'])
      converted_time = convertTime(message_time, utc_offset)
      formatted_datetime = converted_time.strftime("%B, %dth %I:%M %p")
      if type == 'Error':
        st.error(msg+' - '+formatted_datetime)
      elif type  == 'Warning':
        st.warning(msg+' - '+formatted_datetime)
      else:
        st.success(msg+' - '+formatted_datetime)
