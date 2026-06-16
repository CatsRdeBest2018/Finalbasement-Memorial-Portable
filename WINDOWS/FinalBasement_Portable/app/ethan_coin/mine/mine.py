import streamlit as st
from streamlit import session_state
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stateful_button import button
from datetime import datetime
import time
import random
from bson import ObjectId
from funcs import transactCoins, sumBal


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
def mine(userAccount, userCoinSum):
  miningPlaceholder = st.empty()
  
  sum = 0.0
  for coin in EthanCoin.find():
    sum = round(sum+coin['value'],3)
  for coin in Lottery.find():
    sum = round(sum+coin['value'],3)
  
  if round(sum,3) > 1000.0:
    st.error('Threshold reached!')
  else:
    st.write('---')
    def load_miners(cps):
      session_state['loop'] = True
      while True:
        if 'loop' in session_state:
          if session_state['loop'] == False:
            break
  
        div = f"""
        <div style="display: flex; align-items: center;">
            <img src="{get_display_image_src('local_data/files/EthanCoin/MineEthanCoin.png')}" width=192 height=192 style="margin-right: 10px;">
            <div style="display: flex; flex-direction: column;">
                <span style="font-size: 60px; font-weight: bold;">Mining</span>
                <span style="font-size: 20px;">{str(sumBal())+' EC'}</span>
            </div>
        </div>
        """
        miningPlaceholder.markdown(div, unsafe_allow_html=True)
        found = False
        for i in range(len(userAccount['miners'])):
          miner = userAccount['miners'][i]
          if miner['status'] == 'Mining':
            if (datetime.utcnow()-normalize_datetime(miner['time'])).total_seconds() >= 60:
              userAccount['miners'][i]['status'] = 'Sleeping'
              Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'miners': userAccount['miners']}})
              if miner['_id'] in session_state['mining']['clickedMiners']:
                session_state['mining']['clickedMiners'].remove(miner['_id'])
              found = True
        if found:
          st.rerun()
        time.sleep(3)
        found = False
        for userCoin in userAccount['balance']:
          foundCoin = EthanCoin.find_one({'currentId': userCoin['_id']})
          if foundCoin != None:
            if foundCoin['value'] != 1.0:
              newVal = round(foundCoin['value']+cps,3)
              EthanCoin.update_one({'currentId': userCoin['_id']}, {'$set': {'value': newVal}})
              found = True
              currId = foundCoin['currentId']
              break
        if found == False:
          currId = ObjectId()
          EthanCoin.insert_one({'currentId': currId, 'value': cps})
          Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': currId}}})
  
  
    mine = st.button(label='Mine EC '+str(session_state['mining']['clicks'])+'/3')
    if mine:
      session_state['mining']['clicks'] += 1
      if session_state['mining']['clicks'] == 3:
        found = False
        for userCoin in userAccount['balance']:
          foundCoin = EthanCoin.find_one({'currentId': userCoin['_id']})
          if foundCoin != None:
            if foundCoin['value'] != 1.0:
              newVal = round(foundCoin['value']+.001,3)
              EthanCoin.update_one({'currentId': userCoin['_id']}, {'$set': {'value': newVal}})
              found = True
              break
        if found == False:
          currId = ObjectId()
          EthanCoin.insert_one({'currentId': currId, 'value': 0.001})
          Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': currId}}})
        session_state['mining']['clicks'] = 0
      st.rerun()
  
    colored_header(
      label="Miners",
      color_name="violet-70",
      description=None
    )
    userAccount = Accounts.find_one({'_id': session_state['id']})
    cps = 0.0
    div = f"""
    <div style="display: flex; align-items: center;">
        <img src="{get_display_image_src('local_data/files/EthanCoin/MineEthanCoin.png')}" width=192 height=192 style="margin-right: 10px;">
        <div style="display: flex; flex-direction: column;">
            <span style="font-size: 60px; font-weight: bold;">Mining</span>
            <span style="font-size: 20px;">{str(userCoinSum)+' EC'}</span>
        </div>
    </div>
    """
    miningPlaceholder.markdown(div, unsafe_allow_html=True)
    if len(userAccount['miners']) == 0:
      st.error('No miners')
    else:
  
  
      for miner in userAccount['miners']:
  
        st.subheader(miner['name'])
        st.write('Level: '+str(miner['level']))
  
        st.write('Status: '+miner['status'])
        if miner['status'] == 'Mining':
          if miner['_id'] in session_state['mining']['clickedMiners']:
            minerCps = None
            if miner['level'] == 1:
              minerCps = 0.001
            cps = round(cps+minerCps,3)
          else:
            session_state['id'] = None
            st.header('Thanks to Connor Smilie for enforcing people from using multiple tabs!!!!')
            st.write('Thats right little pluh u thought you were smart or sum')
            time.sleep(10)
            st.rerun()
        else:
          if miner['_id'] in session_state['mining']['clickedMiners']:
            session_state['mining']['clickedMiners'].remove(miner['_id'])
        waken = st.button(label='GET BACK TO WOORK BLUD', key=miner['_id'])
        st.write('---')
        if waken:
          userAccount = Accounts.find_one({'_id': userAccount['_id']})

          if 'mining' not in session_state:
            session_state['mining'] = {'clicks': 0, 'clickedMiners': []}

          if 'clickedMiners' not in session_state['mining']:
            session_state['mining']['clickedMiners'] = []

          for i in range(len(userAccount['miners'])):
            loopedMiner = userAccount['miners'][i]

            if loopedMiner['_id'] == miner['_id']:
              # Local DB fix:
              # Update status AND time in the full miners list at once.
              # Do not use Mongo-style nested array update queries here.
              userAccount['miners'][i]['status'] = 'Mining'
              userAccount['miners'][i]['time'] = datetime.utcnow().isoformat()

              Accounts.update_one(
                {'_id': userAccount['_id']},
                {'$set': {'miners': userAccount['miners']}}
              )

              if loopedMiner['_id'] not in session_state['mining']['clickedMiners']:
                session_state['mining']['clickedMiners'].append(loopedMiner['_id'])

              st.rerun()

    colored_header(
      label="Shop",
      color_name="violet-70",
      description=None
    )
    st.subheader('Miner')
    buyMiner = button(label='Buy Miner', key='buyminerbutton')
    if buyMiner:
      buyminerform = st.form('buy-miner-form')
      with buyminerform:
        st.header('Buy miner')
        name = st.text_input('Enter miner name')
        buy = st.form_submit_button(label='Buy 5.0 EC')
  
        if buy:
          if userCoinSum < 5.0:
            st.error('You cant afford '+name)
          else:
            ids = transactCoins(5.0, None, True)
            for coinId in ids:
              EthanCoin.delete_one({'currentId': coinId})
  
            userMiners = userAccount['miners']
            minerIds = []
            for miner in userMiners:
              minerIds.append(miner['_id'])
            while True:
              minerId = ''
              for i in range(5):
                minerId+=str(random.randint(0,9))
              if minerId not in minerIds:
                break
  
            miner = {'_id': minerId, 'name': name, 'level': 1, 'status': 'Sleeping', 'time': datetime.utcnow().isoformat()}
            Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'miners': miner}})
            st.rerun()
  
    if cps != 0.0:
      load_miners(cps)
