import streamlit as st
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
def friends(userAccount, userCoinSum):
  friends = userAccount['friends']
  if len(friends) != 0:
    names = []
    for friend in friends:
  
      friendAccount = Accounts.find_one({'_id': friend['_id']})
      names.append(friendAccount['username'])
      ending = ''
      if friendAccount['active']['online']:
        ending =' (online)'
      else:
        ending =' (offline)'
  
      display = friendAccount['username']+ending
      div = f"""
            <div class="chat-row">
                <img class="chat-icon" src=\"{get_display_image_src(friendAccount['avatarPath'])}\" width=64 height=64>
                <span style="font-size: 20px; font-weight: bold;">{display}</span>
            </div>
            """
  
      st.markdown(div, unsafe_allow_html=True)
      st.write('---')
  
    refresh = st.button('Refresh')
    st.write('---')
    choice = st.selectbox('Choose friend', names)
    friendAccount = Accounts.find_one({'username': choice})
  
    sendcoinsdropdown = st.expander(label='Send Coins to '+friendAccount['username'])
    with sendcoinsdropdown:
      st.subheader('Send Coins')
      st.write('send coins to friend')
      if userCoinSum > 0:
        amount = st.number_input(label='Amount', min_value=0.001, max_value=userCoinSum, step=0.001,key='send')
        message = st.text_input(label='Message', key='messagesend')
        password = st.text_input(label='Enter Password', type='password', key='submitpassword')
        submit = st.button(label='Submit', key='sendsubmit')
        if submit:
          if amount < 0.001 or amount > userCoinSum:
            st.error('bruh')
          else:
            if password != userAccount['password']:
              st.error('incorrect password')
            else:
              st.warning('Loading... (this could take a while depending on your amount, do not close or click anything else)')
              prevUserAmount = userCoinSum
              prevFriendAmount = sumBal(friendAccount)
              transactCoins(amount, friendAccount)
  
              archive = {'userid': userAccount['_id'], 'balSum': prevUserAmount, 'method': 'sendCoins', 'sentUser': friendAccount['_id'], 'sentUserBalSum': prevFriendAmount, 'amount': amount, 'archiveType': 'coinTransaction', 'archiveDate': datetime.utcnow().isoformat()}
              Archives.insert_one(archive)
  
              Accounts.update_one({'_id': friendAccount['_id']}, {'$push': {'transactions': {'msg': userAccount['username']+' Sent you '+str(amount)+ ' EC, \"'+message+'\"', 'type': 'Success', 'time': datetime.utcnow().isoformat()}}})
              Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'transactions': {'msg': 'You sent '+str(amount)+ ' EC to '+friendAccount['username'], 'type': 'Success', 'time': datetime.utcnow().isoformat()}}})
              st.success('Sent!')
      else:
        st.error('Blud has no coins')
    requestcoinsdropdown = st.expander(label='Request Coins from '+friendAccount['username'])
    with requestcoinsdropdown:
      st.subheader('Request Coins')
      st.write('Requests coins from a friend')
  
  
      amount = st.number_input(label='Amount', min_value=0.001, step=0.001, key='request')
      message = st.text_input(label='Message', key='requestmessage')
      submit = st.button(label='Submit', key='requestsubmit')
      if submit:
        if amount < 0.001:
          st.error('bruh')
        else:
          if id_in(userAccount['_id'], [request['_id'] for request in friendAccount['requests']]):
            st.error('You have already requested to this person pluh')
          else:
            requestObj = {'_id': userAccount['_id'], 'msg': message, 'amount': amount, 'date': datetime.utcnow().isoformat()}
            Accounts.update_one({'_id': friendAccount['_id']}, {'$push': {'requests': requestObj}})
            Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'transactions': {'msg': 'You requested '+str(amount)+' EC from: '+friendAccount['username'], 'type': 'Warning', 'time': datetime.utcnow().isoformat()}}})
            st.success('Requested')
  else:
    st.header('No Friends Lol')
    st.write('go add people in the basement view')
  st.write('---')                
  st.header('Requests')
  if len(userAccount['requests']) == 0:
    st.error('No requests')
  else:
    for request in userAccount['requests']:
      requester = Accounts.find_one({'_id': request['_id']})
      div = f"""
      <div style="display: flex; align-items: center;">
          <img src=\"{get_display_image_src(requester['avatarPath'])}\" width=96 height=96 style="margin-right: 10px;">
          <div style="display: flex; flex-direction: column;">
              <span style="font-size: 40px; font-weight: bold;">{requester['username']} - {request['amount']} EC</span>
              <span style="font-size: 20px;">"{request['msg']}"</span>
          </div>
      </div>
      """
      st.markdown(div, unsafe_allow_html=True)
      accept = st.button(label='Accept', key=str(requester['_id'])+'accept')
      decline = st.button(label='Decline', key = str(requester['_id'])+'decline')
      if accept:
        if userCoinSum < request['amount']:
          st.error('You can not afford this 💀')
        else:
          prevUserAmount = userCoinSum
          prevRequesterAmount = sumBal(requester)
          transactCoins(request['amount'], requester)
          Accounts.update_one({'_id': userAccount['_id']}, {'$pull': {'requests': request}})
          Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'transactions': {'msg': 'You accepted '+requester['username']+'\'s request of '+str(request['amount']), 'type': 'Warning', 'time': datetime.utcnow().isoformat()}}})
          Accounts.update_one({'_id': requester['_id']}, {'$push': {'transactions': {'msg': userAccount['username']+' accepted your request of '+str(request['amount']), 'type': 'Success', 'time': datetime.utcnow().isoformat()}}})
  
          archive = {'userid': userAccount['_id'], 'balSum': prevUserAmount, 'method': 'acceptedRequest', 'requester': requester['_id'], 'requesterBalSum': prevRequesterAmount, 'amount': request['amount'], 'archiveType': 'coinTransaction', 'archiveDate': datetime.utcnow().isoformat()}
          Archives.insert_one(archive)
          st.rerun()
      elif decline:
        Accounts.update_one({'_id': userAccount['_id']}, {'$pull': {'requests': request}})
        Accounts.update_one({'_id': requester['_id']}, {'$push': {'transactions': {'msg': userAccount['username']+' declined your request of '+str(request['amount']), 'type': 'Error', 'time': datetime.utcnow().isoformat()}}})
        st.rerun()