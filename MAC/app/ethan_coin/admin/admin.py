import streamlit as st
from streamlit import session_state
from bson import ObjectId
import math
from datetime import datetime


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
def admin(userAccount):
  if session_state['adminKey'] == userAccount['password']:
    st.header('Welcome Master')
    st.write('What do you wish to do today 😩😩😩😩😩')
    st.write('---')

    adminSelect = st.selectbox(label='Pick', options=['Give Coin', 'Delete Coin', 'Add Coin Value', 'Bounties'])


    st.write('---')
    if adminSelect == 'Give Coin':
      givecoinform = st.form('give-coin-form')
      with givecoinform:
        st.subheader('giv coin')
        username = st.text_input(label='Enter Username')
        amount = st.number_input(label='Enter Number', min_value=0.001, step=0.001)
        give = st.form_submit_button(label='Give')
        if give:
          st.warning('Loading (This may take a while...)')
          account = Accounts.find_one({'username': username})

          if account != None:
            allIds = []
            wholes = round(math.floor(amount),3)
            dec = round(amount-wholes,3)

            if wholes != 0.0:
              for i in range(int(wholes)):
                newId = ObjectId()
                EthanCoin.insert_one({'currentId': newId, 'value':1.0})
                Accounts.update_one({'_id': account['_id']}, {'$push': {'balance': {'_id': newId}}})
                thatCoin = EthanCoin.find_one({'currentId': newId})
                allIds.append({'_id': thatCoin['_id']})
            if dec != 0.0:
              newId = ObjectId()
              EthanCoin.insert_one({'currentId': newId, 'value':dec})
              Accounts.update_one({'_id': account['_id']}, {'$push': {'balance': {'_id': newId}}})
              thatCoin = EthanCoin.find_one({'currentId': newId})
              allIds.append({'_id': thatCoin['_id']})
            st.success('Done')
            archive = {'userid': account['_id'], 'username': username, 'coins': allIds, 'archiveType': 'adminCoins', 'archiveDate': datetime.utcnow().isoformat()}
            Archives.insert_one(archive)
          else:
            st.error('No account')
    elif adminSelect == 'Bounties':
      st.header('Bounties')
      bountySelect = st.selectbox(label='Pick', options=['Make Bounty', 'Remove Bounty'])
      if bountySelect == 'Make Bounty':
        makebountyform = st.form('make-bounty-form')
        with makebountyform:
          st.subheader('Make bounty')
          person = st.text_input(label='Enter name')
          reward = st.text_input(label='Enter reward')
          create = st.form_submit_button(label='Create')
          if create:
            bountyObj = {'header': person, 'reward': reward}
            Bounties.insert_one(bountyObj)
            st.write('created')

      elif bountySelect == 'Remove Bounty':
        removebountyform = st.form('remove-bounty-form')
        with removebountyform:
          st.subheader('Remove bounty')
          id = st.text_input('enter id')
          remove = st.form_submit_button(label='Remove')
          if remove:
            bounty = Bounties.find_one({'_id': ObjectId(id)})
            if bounty != None:
              Bounties.delete_one({'_id': bounty['_id']})
              st.success('Deleted')
            else:
              st.error('Not found')
    elif adminSelect == 'Delete Coin':
      st.header('Delete Coin')
      st.write('delete coin')
      method = st.selectbox(label='Method', options=['Load Archive'])
      if method == 'Load Archive':
        loadarchiveform = st.form('load-archive-form')
        with loadarchiveform:
          st.header('Load archive')
          st.write('pluh')

          archiveId = st.text_input(label='Enter ID')
          submit = st.form_submit_button(label='Submit')
          if submit:
            archive = Archives.find_one({'_id': ObjectId(archiveId)})
            if archive == None:
              st.error('Not found')
            else:
              for coin in archive['coins']:
                EthanCoin.delete_one({'_id': coin['_id']})
              st.success('It is done')
    elif adminSelect == 'Add Coin Value':
      st.header('Add coin value')
      st.write('add value')
      addcoinvalueform = st.form('add-coin-value-form')
      with addcoinvalueform:
        st.header('Add coin')
        st.write('hi')
        value = st.number_input(label='Enter Value')
        enter = st.form_submit_button(label='Enter')
        if enter:
          archive= {'value': value, 'archiveType': 'coinValue', 'archiveDate': datetime.utcnow().isoformat()}
          Archives.insert_one(archive)

  else:
    adminKey = st.text_input('passwordd', type='password')
    session_state['adminKey'] = adminKey 
    if adminKey != '':
      st.rerun()
