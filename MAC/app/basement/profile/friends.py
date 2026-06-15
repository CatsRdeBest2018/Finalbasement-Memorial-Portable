import streamlit as st
from streamlit_extras.stateful_button import button
from datetime import datetime

from local_services.local_db import Accounts
from local_services.local_storage import get_display_image_src


def friends(userAccount):
  friends = userAccount['friends']
  if friends == []:
    st.subheader('No Friends?')
    st.write('Go add some')
  else:
    st.subheader('Friends')
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
      friend_avatar = get_display_image_src(friendAccount['avatarPath'])

      div = f"""
            <div class="chat-row">
                <img class="chat-icon" src="{friend_avatar}" width=64 height=64>
                <span style="font-size: 20px; font-weight: bold;">{display}</span>
            </div>
            """

      st.markdown(div, unsafe_allow_html=True)
      st.write('---')

    refresh = st.button('Refresh')
    st.write('---')
    choice = st.selectbox('Choose friend', names)
    unfriend = st.button('Unfriend ' +choice)
    message = button(label='Message '+choice, key='message-friend')
    friendAccount = Accounts.find_one({'username': choice})

    st.write('About me - '+str(friendAccount['aboutMe']))
    if unfriend:
      friendAccount = Accounts.find_one({'username': choice})
      Accounts.update_one({'_id': userAccount['_id']}, {'$pull': {'friends': {'_id': friendAccount['_id']}}})
      Accounts.update_one({'_id': friendAccount['_id']}, {'$pull': {'friends': {'_id': userAccount['_id']}}})
      Accounts.update_one({'_id': friendAccount['_id']}, {'$push': {'inbox': {'msg': userAccount['username']+' has unfriended you bruh', 'type': 'Error', 'time': datetime.utcnow()}}})
      st.rerun()
    if message:
      message_send = st.form('message-send')
      with message_send:
        st.header('Send to '+choice)
        text = st.text_input(label='Send message', max_chars=300)
        press = st.form_submit_button(label='Send')
        if press:
          Accounts.update_one({'_id': Accounts.find_one({'username': choice})['_id']}, {'$push': {'inbox': {'msg': '\"'+text+'\", From: '+userAccount['username'], 'type': 'warning', 'time': datetime.utcnow()}}})
          st.write('Sent')
  st.write('---')
  input_chat = st.form('addfriend-form')
  with input_chat:

    st.markdown('Add Friend')
    cols  = st.columns((6, 1))
    username = cols[0].text_input('Add Friend', label_visibility='collapsed', key='friend_username')
    press = cols[1].form_submit_button('Add')  
    if press:
      friendAccount = Accounts.find_one({'username': username})
      if friendAccount == None:
        st.error('No account found')
      elif friendAccount['_id'] == userAccount['_id']:
        st.error('Bro think he can friend himself 💀💀💀💀')
      elif userAccount['_id'] in [i['_id'] for i in friendAccount['friendRequests']]:
        st.error('You have already friended this person')
      elif friendAccount['_id'] in [i['_id'] for i in userAccount['friendRequests']]:
        st.error('This person has already friended you')
      elif friendAccount['_id'] in [i['_id'] for i in userAccount['friends']]:
        st.error('You are already friends with this person')
      else:
        Accounts.update_one({'_id': friendAccount['_id']}, {'$push': {'friendRequests': {'_id': userAccount['_id']}}})
        st.success('Account friended!')
  st.write('---')
  st.subheader('Friend Requests')
  if len(userAccount['friendRequests']) == 0:
    st.write('No incoming requests')
  else:
    for friend in userAccount['friendRequests']:
      friendAccount = Accounts.find_one({'_id': friend['_id']})
      friend_avatar = get_display_image_src(friendAccount['avatarPath'])

      div = f"""
            <div class="chat-row">
                <img class="chat-icon" src="{friend_avatar}" width=64 height=64>
                <span style="font-size: 20px; font-weight: bold;">{friendAccount['username']} has Friended you</span>
            </div>
            """

      st.markdown(div, unsafe_allow_html=True)

      accept = st.button(label='accept', key=friendAccount['_id'])
      decline = st.button(label='decline', key=str(friendAccount['_id'])+'2')
      if accept or decline:
        Accounts.update_one({'_id': userAccount['_id']}, {'$pull': {'friendRequests': {'_id': friendAccount['_id']}}})
      if decline:
        Accounts.update_one({'_id': friendAccount['_id']}, {'$push': {'inbox': {'msg': userAccount['username']+' Declined your friend request oof', 'type': 'Error', 'time': datetime.utcnow()}}})
      if accept:
        Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'friends':{'_id': friendAccount['_id']}}})
        Accounts.update_one({'_id': friendAccount['_id']}, {'$push': {'friends':{'_id': userAccount['_id']}}})
        Accounts.update_one({'_id': friendAccount['_id']}, {'$push': {'inbox': {'msg': userAccount['username']+' Accepted your friend request yay', 'type': 'Success', 'time': datetime.utcnow()}}})
      if accept or decline:
        st.rerun()

      st.write('---')
