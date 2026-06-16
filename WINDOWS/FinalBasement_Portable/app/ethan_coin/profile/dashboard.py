import streamlit as st
from streamlit import session_state
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stateful_button import button
from datetime import datetime
from bson import ObjectId
import math
import json
import zipfile
import io
from funcs import sumBal, convertTime


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
def dashboard(userAccount, userCoinSum):
  div = f"""
        <div style="display: flex; align-items: center;">
            <img src="{get_display_image_src('local_data/files/EthanCoin/EthanCoin.png')}" width=192 height=192 style="margin-right: 10px;">
            <div style="display: flex; flex-direction: column;">
                <span style="font-size: 40px; font-weight: bold;">{'Ethan Coin Balance'}</span>
                <span style="font-size: 20px;">{str(userCoinSum)+' EC'}</span>
            </div>
        </div>
        """
  st.markdown(div, unsafe_allow_html=True)
  st.write('')
  colored_header(
    label="Options",
    color_name="violet-70",
    description=None
  )
  columns = st.columns(2)
  with columns[0]:
    st.subheader('Deposit:')
    deposit = button(label='Press', key='deposit-ec')
    if deposit:
  
      uploaded_file = st.file_uploader('Upload ZIP file', type=['zip'])
      if uploaded_file:
        prevAmount = userCoinSum
        zip_file_content = uploaded_file.read()
        keys=[]
        with zipfile.ZipFile(io.BytesIO(zip_file_content), 'r') as zip_file:
          for filename in zip_file.namelist():
            with zip_file.open(filename) as file:
              json_data = json.load(file)
              keys.append(json_data['key'])
        userKeys = [coin['_id'] for coin in userAccount['balance']]
        coinIds = []
        for key in keys:
          if not id_in(key, userKeys):
            foundCoin = EthanCoin.find_one({'currentId': key})
            if foundCoin != None:
              coinIds.append(foundCoin['_id'])
              newId = ObjectId()
              EthanCoin.update_one({'currentId': key}, {'$set': {'currentId': newId}})
              Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': newId}}})
        if prevAmount != sumBal():
          archive = {'userid': userAccount['_id'], 'balSum': prevAmount, 'method': 'deposit', 'coinsDeposited': coinIds, 'archiveType': 'coinTransaction', 'archiveDate': datetime.utcnow().isoformat()}
          Archives.insert_one(archive)
        st.rerun()
  
  with columns[1]:
    st.subheader('Withdrawal:')
    withdrawal = button(label='Press1', key='withdrawl-ec')
    if withdrawal:
      if userCoinSum == 0:
        st.error('Nothing to withdrawl')
      else:
 
        amount = st.number_input(label='Amount', min_value=0.001, max_value=userCoinSum, step=0.001)
        all = st.radio(label='Withdrawl All?', options=['No', 'Yes'])
        password = st.text_input(label='Enter Password', type='password')
        submit = st.button(label='Submit')
        if submit:
          if password != userAccount['password']:
            st.error('incorrect password')
          else:
  
            if all == 'Yes':
              amount = userCoinSum
  
  
            whole = math.floor(amount)
            
            dec = round(amount-math.floor(amount),3)
            wholes = []
            decs = []
            for coin in userAccount['balance']:
              foundCoin = EthanCoin.find_one({'currentId': coin['_id']})
              if len(wholes)!=whole:
                if foundCoin['value'] == 1.0:
                  wholes.append(coin['_id'])
                  print('added')
              else:
                break
            
            dec = round(dec+(whole-len(wholes)),3)
            if dec != 0.0:
              while True:
                found=False
  
                for coin in userAccount['balance']:
                  if coin['_id'] in decs:
                    continue
                  foundCoin = EthanCoin.find_one({'currentId': coin['_id']})
                  decSum = round(sum([EthanCoin.find_one({'currentId': coinId})['value'] for coinId in decs]),3)
                  if decSum != dec:
                    if foundCoin['value']!=1.0:
                      if round(decSum+foundCoin['value'],3) <= dec:
                        decs.append(foundCoin['currentId'])
                        found = True
                  else:
                    break
                if found == False:
                  break
              if found == False:
                if decSum != dec:
                  for coin in userAccount['balance']:
                    if coin['_id'] in wholes or coin['_id'] in decs:
                      continue
                    foundCoin = EthanCoin.find_one({'currentId': coin['_id']})
                    if foundCoin['value'] < round(dec-decSum,3):
                      continue
                    EthanCoin.delete_one({'_id': foundCoin['_id']})
                    firstNewId = ObjectId()
                    EthanCoin.insert_one({'currentId': firstNewId, 'value': round(dec-decSum,3)})
                    secondNewId = ObjectId()
                    EthanCoin.insert_one({'currentId': secondNewId, 'value': round(foundCoin['value']-round(dec-decSum,3),3)})
                    Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': secondNewId}}})
                    Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': firstNewId}}})
                    decs.append(firstNewId)
                    break
  
  
            all = wholes+decs
                
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
              for i in range(len(all)):
                json_content = json.dumps({'key': str(all[i])})
                filename = f'ec_file_{i+1}.json'
                zip_file.writestr(filename, json_content)
            zip_content = zip_buffer.getvalue()
  
            st.download_button(
              label='Download',
              data=zip_content,
              file_name='EC-'+str(datetime.utcnow())+'.zip'
            )
  colored_header(
    label="Transactions",
    color_name="violet-70",
    description=None
  )
  amount = len(userAccount['transactions'])
  if amount == 0:
    st.error('No transactions')
  else:
    st.success('You have '+str(amount)+' Transaction(s)')
    clear = st.button('Clear Transactions')
    if clear:
      Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'transactions': []}})
      archiveTransactions = {'userid': userAccount['_id'], 'transactions': userAccount['transactions'], 'archiveType': 'clearedTransactions', 'archiveDate': datetime.utcnow().isoformat()}
      Archives.insert_one(archiveTransactions)
      st.rerun()
  
    transactions = userAccount['transactions']
    transactions.reverse()  
    for message in transactions:
      type = message['type']
      msg = message['msg']
  
      utc_offset = session_state['utcOffset']
  
      converted_time = convertTime(message['time'], utc_offset)
      formatted_datetime = converted_time.strftime("%B, %dth %I:%M %p")
      if type == 'Error':
        st.error(msg+' - '+formatted_datetime)
      elif type  == 'Warning':
        st.warning(msg+' - '+formatted_datetime)
      else:
        st.success(msg+' - '+formatted_datetime)
