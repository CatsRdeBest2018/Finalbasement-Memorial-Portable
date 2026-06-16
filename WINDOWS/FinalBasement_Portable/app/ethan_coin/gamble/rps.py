import streamlit as st
import random
import time
from datetime import datetime
from funcs import gambleTransact


from local_services.local_db import (
  Accounts,
  Sessions,
  Posts,
  Articles,
  Submissions,
  Randoms,
  Suggestions,
  Archives,
  Schedules,
  EthanCoin,
  Bounties,
  Trades,
  Items,
  Lottery,
)
from local_services.local_storage import (
  s3,
  bucket_name,
  get_local_file_url,
  s3_url_to_local_path,
  local_path_to_key,
  get_display_image_src,
)
try:
  from funcs import normalize_datetime
except Exception:
  from datetime import datetime
  def normalize_datetime(value):
    if isinstance(value, datetime):
      if value.tzinfo is not None:
        return value.replace(tzinfo=None)
      return value
    if isinstance(value, dict) and '$date' in value:
      value = value['$date']
    if isinstance(value, str):
      try:
        parsed = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
        if parsed.tzinfo is not None:
          parsed = parsed.replace(tzinfo=None)
        return parsed
      except ValueError:
        pass
    return datetime.utcnow()


def normalize_id(value):
  if isinstance(value, dict) and '$oid' in value:
    return str(value['$oid'])
  return str(value)


def same_id(a, b):
  return normalize_id(a) == normalize_id(b)


def id_in(value, values):
  return normalize_id(value) in [normalize_id(item) for item in values]


def render_media(path, media_type=None):
  if path is None:
    return
  if media_type == 'video':
    try:
      response = s3.get_object(Bucket=bucket_name, Key=local_path_to_key(path))
      st.video(response['Body'].read())
      return
    except Exception:
      st.video(s3_url_to_local_path(path))
      return
  if media_type == 'image':
    st.image(s3_url_to_local_path(path))
    return
  st.video(path)
  st.write(path)


def delete_stored_file(path):
  if path is None:
    return
  try:
    s3.delete_object(Bucket=bucket_name, Key=local_path_to_key(path))
  except Exception:
    pass
def rps(userAccount, userCoinSum):
  theForm = st.empty()
  rpsform = theForm.form('rps-form')
  with rpsform:
    st.header('Rock Paper Scissors')
    st.write('Playe RPS!')
  
    bet = st.number_input(label='Amount to bet', min_value=0.001, max_value=userCoinSum)
    choice = st.selectbox(label='Choose', options=['Rock', 'Paper', 'Scissors'])
    play = st.form_submit_button(label='Play!')
    if play:
      if bet > userCoinSum:
        st.error('Bruh')
      else:
        compChoice = random.choice(['Rock', 'Paper', 'Scissors'])
        compWin = False
        userWin = False
        tie = False
        if choice == 'Rock':
          if compChoice == 'Rock':
            tie = True
          elif compChoice == 'Paper':
            compWin = True
          elif compChoice == 'Scissors':
            userWin = True
        elif choice == 'Paper':
          if compChoice == 'Rock':
            userWin = True
          elif compChoice == 'Paper':
            tie = True
          elif compChoice == 'Scissors':
            compWin = True
        elif choice == 'Scissors':
          if compChoice == 'Rock':
            compWin = True
          elif compChoice == 'Paper':
            userWin = True
          elif compChoice == 'Scissors':
            tie = True
  
        # Balance before the game. On a tie, this stays unchanged.
        prevAmount = userCoinSum
        result = 'tie'

        if tie:
          st.success('I choose '+compChoice)
          st.warning('Tie!')
        else:
          if userWin:
            gambleTransact(True, bet)
            result = 'win'
            st.success('I choose '+compChoice)
            st.success('You win! +'+str(bet)+' EC')
          elif compWin:
            gambleTransact(False, bet)
            result = 'loss'
            st.success('I choose '+compChoice)
            st.error('You lost! -'+str(bet)+' EC')

        archive = {
          'userid': userAccount['_id'],
          'balSum': prevAmount,
          'bet': bet,
          'result': result,
          'method': 'gamble',
          'game': 'rps',
          'compChoice': compChoice,
          'userChoice': choice,
          'archiveType': 'coinTransaction',
          'archiveDate': datetime.utcnow().isoformat()
        }

        Archives.insert_one(archive)
        time.sleep(1)
        st.rerun()
