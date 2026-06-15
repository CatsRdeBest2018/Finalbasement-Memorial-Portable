import streamlit as st
from datetime import datetime
from bson import ObjectId
import math


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
def my_coins(userAccount, userCoinSum):
  st.subheader('Total:')
  st.write(userCoinSum, 'EC')
  st.write('---')
  for i in range(len(userAccount['balance'])):
    foundCoin = EthanCoin.find_one({'currentId': userAccount['balance'][i]['_id']})
    if foundCoin != None:
      div = f'''
            <div style="display: flex; align-items: center;">
                <img src="{get_display_image_src('local_data/files/EthanCoin/EthanCoin.png')}" width=32 height=32 style="margin-right: 10px;">
                <div style="display: flex; flex-direction: column;">
                    <span style="font-size: 20px; font-weight: bold;">Value: {foundCoin['value']}</span>
                    <span style="font-size: 15px;">{'Access Key: '+str(foundCoin['currentId'])}</span>
                </div>
            </div>
            '''
      st.markdown(div, unsafe_allow_html=True, help='You have a coin, but it\'s only worth this value. Also don\'t let anybody see these keys.')
      st.write('\n')
  st.write('---')
  combine = st.button(label='Combine decimals')
  st.button(label='Refresh')
  if combine:
    subvalue = 0
    for coin in userAccount['balance']:
      foundCoin = EthanCoin.find_one({'currentId': coin['_id']})
      if foundCoin['value'] != 1.0:
        subvalue = round(subvalue+foundCoin['value'],3)
        EthanCoin.delete_one({'_id': foundCoin['_id']})
    wholes = int(round(math.floor(subvalue),3))
    dec = round(subvalue-wholes,3)
    if wholes != 0:
      for i in range(wholes):
        newId = ObjectId()
        EthanCoin.insert_one({'currentId': newId, 'value': 1.0})
        Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': newId}}})
    if dec != 0:
      newId = ObjectId()
      EthanCoin.insert_one({'currentId': newId, 'value': dec})
      Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': newId}}})
    st.rerun()
  st.write('---')
  redeemcoinform = st.form('redeem-coin-form')
  with redeemcoinform:
    st.subheader('Redeem Coin')
    st.markdown('Enter in an id', unsafe_allow_html=True, help='DO NOT REDEEM THE CARD MA\'AM')
    id = st.text_input(label='ID')
    redeem = st.form_submit_button(label='Redeem')
    if redeem:
      worked = True
      try:
        objId = ObjectId(id)
      except:
        st.error('Please enter a valid id')
        worked = False
      if worked:
        foundCoin = EthanCoin.find_one({'currentId': objId})
        if foundCoin == None:
          st.error('Please enter a valid id')
        else:
          if id_in(foundCoin['currentId'], [coin['_id'] for coin in userAccount['balance']]):
            st.error('You already own this coin pal')
          else:
            prevAmount = userCoinSum
            newId = ObjectId()
            EthanCoin.update_one({'_id': foundCoin['_id']}, {'$set': {'currentId': newId}})
            Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': newId}}})
            Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'transactions': {'msg': 'You redeemed EC worth: '+str(foundCoin['value']), 'type': 'Success', 'time': datetime.utcnow().isoformat()}}})
            st.success('Added!')
  
            archive = {'userid': userAccount['_id'], 'balSum': prevAmount, 'method': 'redeemCoin', 'coin_id': foundCoin['_id'], 'archiveType': 'coinTransaction', 'archiveDate': datetime.utcnow().isoformat()}
            Archives.insert_one(archive)
            st.rerun()
  st.write('---')
  removecoinform = st.form('remove-coin-form')
  with removecoinform:
    st.subheader('Remove Coin')
    st.write('Remove coin from your account')
    id = st.text_input(label='ID')
    remove = st.form_submit_button(label='Remove')
    if remove:
      worked = True
      try:
        objId = ObjectId(id)
      except:
        st.error('Please enter a valid id')
        worked = False
      if worked:
        prevAmount = userCoinSum
        foundCoin = EthanCoin.find_one({'currentId': objId})
        if foundCoin == None:
          st.error('Please enter a valid id')
        else:
          if not id_in(foundCoin['currentId'], [coin['_id'] for coin in userAccount['balance']]):
            st.error('...')
          else:
            Accounts.update_one({'_id': userAccount['_id']}, {'$pull': {'balance': {'_id': foundCoin['currentId']}}})
            Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'transactions': {'msg': 'You removed EC worth: '+str(foundCoin['value']), 'type': 'Warning', 'time': datetime.utcnow().isoformat()}}})
            st.success('Removed')
            archive = {'userid': userAccount['_id'], 'balSum': prevAmount, 'method': 'removeCoin', 'coin_id': foundCoin['_id'], 'archiveType': 'coinTransaction', 'archiveDate': datetime.utcnow().isoformat()}
            Archives.insert_one(archive)
            st.rerun()
