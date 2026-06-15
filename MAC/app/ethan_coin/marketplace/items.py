import streamlit as st
from streamlit import session_state
from datetime import datetime
from funcs import sumBal, transactCoins


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
def items(userAccount, userCoinSum):
  items = list(Items.find())
  if len(items) == 0:
    st.error('Nothing being sold right now')
  else:
    privacyKey = st.text_input(label='Enter Privacy Key')
    st.write('---')
    if privacyKey == '' or session_state['prevTab']['sub1'] != 'Marketplace':
      session_state['itemPrivacyKey'] = None
    else:
      session_state['itemPrivacyKey'] = privacyKey
  
  
    items.reverse()
    for item in items:
      if privacyKey != None:
        if item['privacyKey'] != session_state['itemPrivacyKey']:
          continue
      st.subheader(item['title'])
      st.write(item['description'])
      itemAccount = Accounts.find_one({'_id': item['userid']})
      if item['thumbnail'] != None:
        if item['thumbnailType'] == 'video':
          render_media(item['thumbnail'], 'video')
        elif item['thumbnailType'] == 'image':
          st.image(s3_url_to_local_path(item['thumbnail']))
  
      itemDate = normalize_datetime(item['date'])
      extra = ''
      if userAccount['status'] == 'Admin':
        extra = ' • Item ID '+str(item['_id'])
      if item['digital'] == None:
        type = 'PHYSICAL'
      else:
        type = 'DIGITAL'
  
      div = f"""
            <div class="chat-row">
              <img class="chat-icon" src=\"{get_display_image_src(itemAccount['avatarPath'])}\" width=32 height=32>
              {itemAccount['username']+' • Sold '+str(len(item['buyers']))+' Times • '+type+' • '+normalize_datetime(item['date']).strftime('%B %dth, %Y')+extra}
              </div>
            </div>
            """
  
      st.markdown(div, unsafe_allow_html=True)
      st.write(' ')
      buyerIds = [buyer['_id'] for buyer in item['buyers']]
      if not id_in(userAccount['_id'], buyerIds) and not same_id(userAccount['_id'], item['userid']):
        buy = st.button(label='BUY '+str(item['price'])+' EC', key=str(item['_id']))
        if buy:
          if userCoinSum < item['price']:
            st.error('Not enough EC pluh')
          else:
            prevAmount = userCoinSum
            sellerAmount = sumBal(itemAccount)
            transactCoins(item['price'], itemAccount)
            Items.update_one({'_id': item['_id']}, {'$push': {'buyers': {'_id': userAccount['_id'], 'date': datetime.utcnow().isoformat()}}})
            Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'transactions': {'msg': 'You purchased item \"'+item['title']+'\" for '+str(item['price'])+' EC from '+itemAccount['username'], 'type': 'Warning', 'time': datetime.utcnow().isoformat()}}})
            Accounts.update_one({'_id': itemAccount['_id']}, {'$push': {'transactions': {'msg': 'Your item \"'+item['title']+'\" was purchased by '+userAccount['username']+' for '+str(item['price'])+' EC', 'type': 'Success', 'time': datetime.utcnow().isoformat()}}})
            archive = {'userid': userAccount['_id'], 'balSum': prevAmount, 'method': 'buyItem', 'itemBought': item['_id'], 'price': item['price'], 'sellerBalSum': sellerAmount, 'archiveType': 'coinTransaction', 'archiveDate': datetime.utcnow().isoformat()}
            Archives.insert_one(archive)
            st.rerun()
      else:
        if item['digital'] == None:
          if not same_id(item['userid'], userAccount['_id']):
            st.success('You have purchased this item')
        else:
          digitalItemsDropdown = st.expander(label='Digital Items')
          with digitalItemsDropdown:
            if item['digital']['text'] != None:
              st.subheader(item['digital']['text'])
            else:
              st.subheader('No text')
            st.write('---')
            if item['digital']['content'] != None:
  
              if item['digital']['contentType'] == 'video':
                render_media(item['digital']['content'], 'video')
              elif item['digital']['contentType'] == 'image':
                st.image(s3_url_to_local_path(item['digital']['content']))
              st.write('---')
            if item['digital']['file'] != None:
              st.subheader('One available file')
              st.write(item['digital']['file'])
  
      st.write('---')
