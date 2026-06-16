import streamlit as st
from streamlit import session_state
from PIL import Image, ImageDraw
import time
import random
from streamlit_extras.let_it_rain import rain
from datetime import datetime, timedelta
import math
from bson import ObjectId

from local_services.local_db import (
  Accounts,
  Sessions,
  Randoms,
  EthanCoin,
  Lottery,
)
from local_services.local_storage import get_local_file_url, s3_url_to_local_path, get_display_image_src

def normalize_datetime(value):
  if isinstance(value, datetime):
    if value.tzinfo is not None:
      return value.replace(tzinfo=None)
    return value

  if isinstance(value, dict) and '$date' in value:
    value = value['$date']

  if isinstance(value, str):
    cleaned = value.strip().replace('Z', '+00:00')
    try:
      parsed = datetime.fromisoformat(cleaned)
      if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
      return parsed
    except ValueError:
      pass

  return datetime.utcnow()


def convertTime(origTime, utcOffset):
  origTime = normalize_datetime(origTime)

  if utcOffset[0] == '-':
    hours = int(utcOffset[1:3]) * -1
    minutes = int(utcOffset[3:5]) * -1
  else:
    hours = int(utcOffset[1:3])
    minutes = int(utcOffset[3:5])

  offset_timedelta = timedelta(hours=hours, minutes=minutes)

  return origTime + offset_timedelta
def createAvatar(img):
  size = 1000
  img.thumbnail((size, size))

  circle_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))

  mask_size = (size, size)
  mask = Image.new('L', mask_size, 0)
  mask_draw = ImageDraw.Draw(mask)
  mask_draw.ellipse((0, 0) + mask_size, fill=255)

  resized_image = img.resize(mask_size)

  masked_image = Image.new('RGBA', mask_size)
  masked_image.paste(resized_image, (0, 0), mask=mask)
  circle_image.paste(masked_image, (0, 0), mask=mask)

  return circle_image
def openSession(sessionId, tab):
  t1=time.time()

  session = Sessions.find_one({'_id': sessionId})
  if session == None:
    return False
  userAccount = Accounts.find_one({'_id': session_state['id']})
  sessionPeople = session['people']

  st.header(session['title'])

  st.write(session['description'])

  if session_state['currentSession'] == None:
    session_state['currentSession'] = {'_id': sessionId, 'origLength': len(session['history']), 'idle': False, 'tab': tab, 'isRandom': session['isRandom']}

  if tab != 'ghost':
    personObj = {'_id': userAccount['_id'], 'username': userAccount['username'], 'date': datetime.utcnow()}
    if userAccount['_id'] not in [person['_id'] for person in sessionPeople] and session_state['currentSession']['idle'] == False:

      Sessions.update_one({'_id': sessionId}, {'$push': {'people': personObj}})


  chat_placeholder = st.container()
  input_chat = st.form('chat-form')

  def update_chat():
    global t2

    prev = None
    prevPeople = None
    printed = []

    actives = st.empty()
    warning = st.empty()
    while True:

      time.sleep(.5)
      t2 = time.time()
      if t2-t1 > 180:
        st.error('Kicked (Idle)')
        session_state['currentSession']['idle'] = True
        break
      newSession = Sessions.find_one({'_id': sessionId})
      newPeople = newSession['people']
      newHistory = newSession['history']

      if prev != newHistory:
        prev = newHistory
        if 'currentSession' not in session_state:
          continue
        msgs = newHistory[session_state['currentSession']['origLength']-5:]
        with chat_placeholder:
          for chat in msgs:
            if chat in printed:
              continue
            printed.append(chat)
            current_time = normalize_datetime(chat['date'])
            utc_offset = session_state['utcOffset']
            converted_time = convertTime(current_time, utc_offset)

            formatted_datetime = converted_time.strftime("%B, %dth %I:%M %p")

            if (datetime.utcnow() - current_time).total_seconds() < 2:
              if chat['text'].startswith('!rain'):

                emoji = chat['text'][5:]

                try:
                  rain(
                    emoji=emoji,
                    font_size=54,
                    falling_speed=5,
                    animation_length=1
                  )
                except Exception as e:
                  print(e)
                  pass


            if newSession['isRandom']:
              userAvatar = get_display_image_src('https://finalbasementbucket.s3.us-east-2.amazonaws.com/profile-images/guest.png')
              if chat['username'] == userAccount['username']:
                userDisplayName = 'You'
              else:
                userDisplayName = 'Random'
            else:
              userDisplayName = chat['username']
              userAvatar = get_display_image_src(chat['path'])
            div = f"""
              <div class="chat-row">
                  <img class="chat-icon" src="{userAvatar}" width=32 height=32>
                  {userDisplayName+': '+chat['text']}
                  </div>

              </div>
                  """
            st.markdown(div, unsafe_allow_html=True, help=formatted_datetime)
            st.write('')

      if prevPeople != newPeople and newSession['isRandom'] == False:
        prevPeople = newPeople
        peopleLst = [person['username'] for person in newPeople]
        actives.write('Current Active People: '+', '.join(peopleLst))
        warning.markdown('**May not be accurate**', help='People might be non-active but still able to view the chat')

  if tab != 'ghost':
    with input_chat:
      text = '**Chat**'
      if session['_id'] != 'OMEGA_CHAT' and session['isRandom'] == False:
        text+=' - Id: '+session['_id']
      st.markdown(text)
      cols = st.columns((6, 1))
      content = cols[0].text_input('Chat', label_visibility='collapsed')
      press = cols[1].form_submit_button('Send')



      if press and session_state['currentSession']['idle'] == False:
        if session_state['currentSession']['idle'] == True:
          return
        current = Sessions.find_one({'_id': sessionId})['history']
        allCodes = [msg['_id'] for msg in current]
        while True:
          code = ''
          for i in range(5):
            code+=str(random.randint(0,9))
          if code not in allCodes:
            break


        textObject = {'_id': code, 'text': content, 'userid': userAccount['_id'], 'username': userAccount['username'], 'path': userAccount['avatarPath'], 'date': datetime.utcnow()}

        texts = []
        for i in range(len(current)):
          if current[i]['userid'] == session_state['id']:
            texts.append(current[i])

        if len(texts) > 3:
          texts.reverse()

          for i in range(len(texts)-1):
            older_date = normalize_datetime(texts[i+1]['date'])
            newer_date = normalize_datetime(texts[i]['date'])

            if (newer_date - older_date).total_seconds() < 1:
              # return 'spam'
              pass

        Sessions.update_one({'_id': sessionId}, {'$push': {'history': textObject}})
        t2=time.time()
        st.rerun()


  update_chat()
def closeSession():
  session_state['loop'] = False
  session_state['begin-random'] = False
  for randomSession in Randoms.find():
    if randomSession['_id'] == session_state['id']:
      Randoms.delete_one({'_id': randomSession['_id']})
  if session_state['currentSession'] != None:
    id = session_state['currentSession']['_id']
    session = Sessions.find_one({'_id': id})
    if session['isRandom']:
      while True:
        code = ''
        for i in range(5):
          code+=str(random.randint(0,9))
        if code not in [i['_id'] for i in session['history']]:
          break
      Sessions.update_one({'_id': id}, {'$push': {'history': {'_id': code, 'text': 'Random left the Chat... Press Continue for more.', 'userid': None, 'username': 'Server', 'path': get_local_file_url('profile-images/guest.png'), 'date': datetime.utcnow()}}})
    for person in session['people']:
      if person['_id'] == session_state['id']:
        Sessions.update_one({'_id': id}, {'$pull': {'people': person}})
        break
    session_state['currentSession'] = None

def sumBal(account = None):
  if account == None:
    account = Accounts.find_one({'_id': session_state['id']})
  bal = list(account['balance'])
  amount=0.0
  for coin in bal:
    foundCoin = EthanCoin.find_one({'currentId': coin['_id']})

    if foundCoin == None:
      Accounts.update_one({'_id': account['_id']}, {'$pull': {'balance': {'_id': coin['_id']}}})
    else:
      amount = round(amount+round(foundCoin['value'], 3),3)
  return round(amount,3)
  
def transactCoins(amount, otherAccount, returnIds = False):
  userAccount = Accounts.find_one({'_id': session_state['id']})
  whole = math.floor(amount)
  dec = round(amount-math.floor(amount),3)
  wholes = []
  decs = []
  for coin in userAccount['balance']:
    foundCoin = EthanCoin.find_one({'currentId': coin['_id']})
    if len(wholes)!=whole:
      if foundCoin['value'] == 1.0:
        wholes.append(coin['_id'])

  dec = round(dec+(whole-len(wholes)),3)
  if dec != 0.0:
    while True:
      found=False

      for coin in userAccount['balance']:
        sumBal()
        if coin['_id'] in decs:
          continue
        foundCoin = EthanCoin.find_one({'currentId': coin['_id']})
        decSum = round(sum([EthanCoin.find_one({'currentId': coinId})['value'] for coinId in decs]),3)
        if dec != 0.0 and decSum != dec:
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

          EthanCoin.delete_one({'_id': foundCoin['_id']})
          if foundCoin['value'] < round(dec-decSum,3):
            continue
          firstNewId = ObjectId()
          EthanCoin.insert_one({'currentId': firstNewId, 'value': round(dec-decSum,3)})
          secondNewId = ObjectId()
          EthanCoin.insert_one({'currentId': secondNewId, 'value': round(foundCoin['value']-round(dec-decSum,3),3)})
          Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': secondNewId}}})
          Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': firstNewId}}})
          decs.append(firstNewId)
          break


  all = wholes+decs
  if returnIds == True:
    return all
  for coinId in all:
    foundCoin = EthanCoin.find_one({'currentId': coinId})
    if foundCoin != None:
      Accounts.update_one({'_id': userAccount['_id']}, {'$pull': {'balance': {'_id': coinId}}})
      newId = ObjectId()
      EthanCoin.update_one({'_id': foundCoin['_id']}, {'$set': {'currentId': newId}})
      Accounts.update_one({'_id': otherAccount['_id']}, {'$push': {'balance': {'_id': newId}}})

def gambleTransact(win, amount):
  userAccount = Accounts.find_one({'_id': session_state['id']})
  if win:

    wholes = round(math.floor(amount),3)
    dec = round(amount-wholes,3)

    if wholes != 0.0:
      for i in range(int(wholes)):
        newId = ObjectId()
        EthanCoin.insert_one({'currentId': newId, 'value':1.0})
        Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': newId}}})

    if dec != 0.0:
      newId = ObjectId()
      EthanCoin.insert_one({'currentId': newId, 'value':dec})
      Accounts.update_one({'_id': userAccount['_id']}, {'$push': {'balance': {'_id': newId}}})
      
  else:
    coinIds = transactCoins(amount, None, True)
    for coinId in coinIds:
      newId = ObjectId()
      coin = EthanCoin.find_one({'currentId': coinId})
      Lottery.insert_one({'_id': coin['_id'], 'currentId': newId, 'value': coin['value']})
      EthanCoin.delete_one({'_id': coin['_id']})