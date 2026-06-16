import warnings

import streamlit as st

# Compatibility patch for old Streamlit packages.
# Some old streamlit_extras components still call st.experimental_rerun(),
# but newer Streamlit versions use st.rerun().
if not hasattr(st, "experimental_rerun") and hasattr(st, "rerun"):
  st.experimental_rerun = st.rerun

from streamlit import session_state

st.set_page_config(page_title='The Basement', page_icon=':left_speech_bubble:', layout='wide')
file_name = 'style.css'

with open(file_name) as f:
  st.markdown(f'<style>{f.read()}/style>', unsafe_allow_html=True)

if 'access' not in session_state:
  session_state['access'] = False

if session_state['access'] == False:
  st.header('🪦 Rip basement')
  st.write('This is much sad')
  st.write('---')
  st.write('Due to some events the basement has been terminated. I did not delete it or anything it just cannot be open for public use.')
  st.write('---')

  joe = 'data:image/jpeg;base64,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'
    
  div = f"""
  <div class="chat-row">
      <img class="chat-icon" src="{joe}" width=128 height=128>

  </div>
  """
  
  st.markdown(div, unsafe_allow_html=True)

  st.write('*\"Sometimes its not the destination, its the friends we made on the way"* - Joe Biren')
  trump = 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Official_Presidential_Portrait_of_President_Donald_J._Trump_%282025%29_%28cropped%29%282%29.jpg/250px-Official_Presidential_Portrait_of_President_Donald_J._Trump_%282025%29_%28cropped%29%282%29.jpg'
  div2 = f"""
  <div class="chat-row">
      <img class="chat-icon" src="{trump}" width=128 height=128>

  </div>
  """
  
  st.markdown(div2, unsafe_allow_html=True)

  st.write('*\"Dont be sad because over, be happy because it happend"* - Donald Pump')
  obama = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQvCad5_N9MVoCbF4ntoqg4JKTxrw-LJDDz956GNlSQRhDpnLBX_adEuwlf2viPE9crDw&usqp=CAU'
  div3 = f"""
  <div class="chat-row">
      <img class="chat-icon" src="{obama}" width=128 height=128>

  </div>
  """
  st.markdown(div3, unsafe_allow_html=True)
  st.write('*\"If you want any cash back come to ethan onysko."* - Barack Obamna.')
  st.write('---')
  password = st.text_input(label='passowrd')
  if password == '1459684':
    session_state['access'] = True
    st.rerun()
else:
  from PIL import Image
  import time
  from streamlit_option_menu import option_menu
  from streamlit_extras.mention import mention
  import random
  from io import BytesIO
  from datetime import datetime
  import pytz
  from funcs import closeSession, createAvatar, sumBal
  from local_services.local_db import Accounts
  from local_services.local_storage import s3, bucket_name, region_name, get_local_file_url, get_display_image_src
  
  warnings.filterwarnings("ignore", category=DeprecationWarning)
  warnings.filterwarnings("ignore", message=".*datetime.datetime.utcnow.*")

  headers = st.context.headers
  
  if 'X-Forwarded-For' in headers:
    ip_address = headers['X-Forwarded-For']
    print(ip_address)
  
  def local_css(file_name):
    with open(file_name) as f:
      st.markdown(f'<style>{f.read()}/style>', unsafe_allow_html=True)
  local_css('style.css')
  
  if 'loop' not in session_state:
    session_state['loop'] = False
  if 'posted' not in session_state:
    session_state['posted'] = False
  if 'id' not in session_state:
    session_state['id'] = None
  if 'currentSession' not in session_state:
    session_state['currentSession'] = None
  if 'utcOffset' not in session_state:
    timezone_name = "US/Eastern"
    current_time = datetime.now(pytz.timezone(timezone_name))
    utc_offset_seconds = current_time.utcoffset().total_seconds()
    formatted_utc_offset = "{:0=+03d}{:02d}".format(int(utc_offset_seconds // 3600), int((utc_offset_seconds % 3600) // 60))
    session_state['utcOffset'] = formatted_utc_offset
  if 'adminKey' not in session_state:
    session_state['adminKey'] = None
    session_state['schedule'] = {'periodOffset': 0}
  if 'prevTab' not in session_state:
    session_state['prevTab'] = {'main': None, 'sub1': None, 'sub2': None, 'sub3': None, 'sub4': None, 'sub5': None}
  if 'itemPrivacyKey' not in session_state:
    session_state['itemPrivacyKey'] = None
  if 'mining' not in session_state:
    session_state['mining'] = {'clicks': 0, 'clickedMiners': []}
  if session_state['id'] == None:
  
    homepage = st.empty()
    with homepage.container():
      st.subheader('Welcome people :wave:')
      n=0
      for account in Accounts.find():
        if account['active']['online']:
          n+=1
      st.title('The Basement ('+str(n)+' Online)')
      st.write('made by me')
  
      # with image_column:
      #   # st.image('https://finalbasementbucket.s3.us-east-2.amazonaws.com/post-content/mewing-cat-mewing_27130.png')
      #   pass
      mention(
      label='Click for Cake!',
      icon='🎂',
      url='https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUXbmV2ZXIgZ3VubmEgZ2l2ZSB5b3UgdXA%3D'
      )
      selectbox = st.empty()
      choice = selectbox.radio(
        'Enter',
        ('Log In', 'Sign Up')
      )
  
      if choice == 'Log In':
        login = st.form('login_form')
  
        with login:
          st.subheader('Log In')
  
          username = st.text_input('Username')
          password = st.text_input('Password', type='password')
          submit_placeholder = st.empty()
          press = submit_placeholder.form_submit_button(label='Log In')
  
          msg = st.empty()
          if press == False:
            msg.warning('Please Enter your Username and Password, or Sign Up')
  
          if press and session_state['id'] == None:
            account = Accounts.find_one({'username': username, 'password': password})
            if account == None:
              msg.error('Incorrect Username/Password')
            else:
              i=3
              session_state['id'] = account['_id']
              submit_placeholder.empty()
              selectbox.empty()
              while True:
                msg.success('Succesfuly Logged In! <'+str(i)+'>')
                i-=1
                time.sleep(1)
                if i < 0:
                  break
              homepage.empty()
              st.rerun()
      else:
        signup = st.form('sign_form')
        with signup:
          st.subheader('Sign up')
          username = st.text_input('Enter a Username', max_chars=32)
          password = st.text_input('Enter a Password', type='password')
          pfp = st.file_uploader('Upload Profile Picture', type=['jpg', 'png'])
          agree = st.checkbox(label='I have read and agreed to the Terms of Service')
          terms = st.expander(label='Terms of Service')
  
          with terms:
            with open('tos.html', 'r') as file:
              html_code = file.read()
              st.markdown(html_code, unsafe_allow_html=True)
  
          submit_placeholder = st.empty()
          press = submit_placeholder.form_submit_button(label='Sign Up')
  
          msg = st.empty()
          if press == False:
            msg.warning('Enter a Username, Password, and Avatar')
          if press:
  
            allUsernames = [i['username'] for i in Accounts.find()]
            if '  ' in username:
              st.error('Username cannot have spaces next to eachother')
            else:
              if len(username) > 32:
                msg.error('Username must be under 32 characters')
              elif len(username) < 3:
                msg.error('Username must be at least 3 characters long')
              elif username in allUsernames:
                msg.error('Username taken lol')
              elif password == '':
                msg.error('Enter Password')
              elif agree != True:
                msg.error('Please read and accept the Terms of Service')
              else:
                if pfp != None:
                  bytes_data = pfp.read()
                  img = Image.open(BytesIO(bytes_data))
                  circleImage = createAvatar(img)
  
                  response = s3.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix='profile-images'
                  )
                  file_names = [obj['Key'][:-4] for obj in response.get('Contents', [])]
  
                  while True:
                    code = ''
                    for i in range(6):
                      code += str(random.randint(0,9))
                    if code not in file_names:
                      break
                  with BytesIO() as temp_buffer:
                    circleImage.save(temp_buffer, format='PNG')
                    temp_buffer.seek(0)
  
                    s3_key = 'profile-images/'+code+'.png'
                    s3.upload_fileobj(temp_buffer, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})
                else:
                  s3_key = 'profile-images/guest.png'
                image_url = get_local_file_url(s3_key)
                account = {'username': username, 'password': password, 'aboutMe': None, 'avatarPath': image_url, 'friends': [], 'friendRequests': [], 'inbox': [], 'balance': [], 'requests': [], 'transactions': [], 'onLeaderboard': False, 'miners': [], 'status': 'Peasent', 'active': {'online': True, 'date': datetime.utcnow()}, 'dateCreated': datetime.utcnow()}
                Accounts.insert_one(account)
                session_state['id'] = Accounts.find_one({'username': username, 'password': password})['_id']
                submit_placeholder.empty()
                selectbox.empty()
                i = 3
                while True:
                  msg.success('Signed Up <'+str(i)+'>')
                  i-=1
                  if i < 0:
                    break
                  time.sleep(1)
                homepage.empty()
                st.rerun()
  else:
    userAccount = Accounts.find_one({'_id': session_state['id']})
    Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'active': {'online': True, 'date': datetime.utcnow()}}})
    with st.sidebar:
      view = option_menu(
        menu_title='View',
        options=['Basement', 'EthanCoin'],
        orientation = 'horizontal'
      )
      if view == 'Basement':
        menuOptions = ['Profile', 'Chatrooms', 'News', 'Suggestions', '------------------------------------', 'Posts', 'Randoms', 'Schedules']
        if userAccount['status'] == 'Admin':
          menuOptions.append('Admin')
        selected = option_menu(
          menu_title='The Basement',
          options=menuOptions
        )
      elif view == 'EthanCoin':
        coinOptions = ['Profile', 'Mine', 'Charts', 'Bounties', 'Trading', 'Gamble', 'Marketplace']
        if userAccount['status'] == 'Admin':
          coinOptions.append('Admin')
        selected = option_menu(
          menu_title='Ethan Coin',
          options=coinOptions
        )
    if view == 'Basement':
      session_state['loop'] = False
      session_state['prevTab']['main'] = 'Basement'
      
      if selected == 'Profile':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Profile'
        closeSession()
  
        profile_selected = option_menu(
          menu_title='Profile',
          options=['Dashboard', 'Friends', 'Inbox'],
          orientation='horizontal'
        )
        st.write('---')
        
        if profile_selected == 'Dashboard':
          session_state['prevTab']['sub2'] = 'Dashboard'
          
          from basement.profile.dashboard import dashboard
          dashboard(userAccount)
        elif profile_selected == 'Friends':
          session_state['prevTab']['sub2'] = 'Friends'
          
          from basement.profile.friends import friends
          friends(userAccount)
        elif profile_selected == 'Inbox':
          session_state['prevTab']['sub2'] = 'Inbox'
  
          from basement.profile.inbox import inbox
          inbox(userAccount)        
      elif selected == 'Chatrooms':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Chatrooms'
        chatrooms_selected = option_menu(
          menu_title='Chatrooms',
          options=['Omega Chat!', 'Chatz!'],
          orientation='horizontal'
        )
        st.write('---')
        
        if chatrooms_selected == 'Omega Chat!':
          session_state['prevTab']['sub2'] = 'Omega Chat!'
          
          from basement.chatrooms.omega_chat import omega_chat
          omega_chat()
          
        elif chatrooms_selected == 'Chatz!':
          session_state['prevTab']['sub2'] = 'Chatz!'
  
          from basement.chatrooms.chatz import chatz
          chatz(userAccount)        
      elif selected == 'News':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'News'
        st.header('News')
        st.write('Some current events that have been publicly uploaded')
        c = st.selectbox(label='View mode', options=['Articles', 'Submit', 'Accept'])
        st.write('---')
        if c == 'Articles':
          session_state['prevTab']['sub2'] = 'Articles'
  
          from basement.news.articles import articles
          articles(userAccount)
  
        elif c == 'Submit':
          session_state['prevTab']['sub2'] = 'Submit'
          
          from basement.news.submit import submit
          submit(userAccount)
        elif c == 'Accept':
          if userAccount['status'] == 'Peasent':
            st.error('you cant use this bish')
          else:
            from basement.news.accept import accept
            accept(userAccount)                  
      elif selected == 'Suggestions':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Suggestions'
        closeSession()
        
        from basement.suggestions.suggestions import suggestions
        suggestions(userAccount)      
      elif selected == 'Posts':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Posts'
        closeSession()
        
        st.header('Posts')
        st.write('Post stuff idk')
        p = st.selectbox(label='View Mode', options=['Scroll', 'Post', 'Manage'])
        st.write('---')
        if p == 'Scroll':
          session_state['prevTab']['sub2'] = 'Scroll'
  
          from basement.posts.scroll import scroll
          scroll(userAccount)
        elif p == 'Post':
          session_state['prevTab']['sub2'] = 'Post'
  
          from basement.posts.post import post
          post(userAccount)
          
        elif p == 'Manage':
          session_state['prevTab']['sub2'] = 'Manage'
  
          from basement.posts.manage import manage
          manage(userAccount)
      elif selected == 'Randoms':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Randoms'
  
        from basement.randoms.randoms import randoms
        randoms(userAccount)      
      elif selected == 'Schedules':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Schedules'
        closeSession()
  
        from basement.schedules.schedules import schedules
        schedules(userAccount)
      elif selected == 'Admin':
        closeSession()
        session_state['loop'] = False
        if session_state['prevTab']['sub1'] != 'Admin':
          session_state['adminKey'] = None
        session_state['prevTab']['sub1'] = 'Admin'
        
        from basement.admin.admin import admin
        admin(userAccount)
    elif view == 'EthanCoin':
      session_state['prevTab']['main'] = 'EthanCoin'
      closeSession()
      
      userCoinSum=sumBal()
      if selected == 'Profile':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Profile'
        profile_selected = option_menu(
          menu_title='Profile',
          options=['Dashboard', 'My Coins', 'Friends'],
          orientation='horizontal'
        )
        st.write('---')
        if profile_selected == 'Dashboard':
          session_state['prevTab']['sub2'] = 'Dashboard'
  
          from ethan_coin.profile.dashboard import dashboard
          dashboard(userAccount, userCoinSum)
          
        elif profile_selected == 'My Coins':
          session_state['prevTab']['sub2'] = 'My Coins'
  
          from ethan_coin.profile.my_coins import my_coins
          my_coins(userAccount, userCoinSum)
        elif profile_selected == 'Friends':
          session_state['prevTab']['sub2'] =  'Friends'
  
          from ethan_coin.profile.friends import friends
          friends(userAccount, userCoinSum)
      elif selected == 'Mine':
        if session_state['prevTab']['sub1'] != 'Mine':
          session_state['mining']['clicks'] = 0
          theMiners = []
          session_state['loop'] = False
  
        session_state['prevTab']['sub1'] = 'Mine'
        from ethan_coin.mine.mine import mine
        mine(userAccount, userCoinSum)
      elif selected == 'Charts':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Charts'
  
        from ethan_coin.charts.charts import charts
        charts(userAccount)
      elif selected == 'Bounties':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Bounties'
  
        from ethan_coin.bounties.bounties import bounties
        bounties(userAccount)
      elif selected == 'Trading':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Trades'
        st.header('Trade EC for cash')
        st.write('Come to me (Ethan) for a straight deal or try to trade with someone else')
        st.write('---')
        view = st.selectbox(label='View', options=['Trades', 'Make Trade', 'Manage'])
        if view == 'Trades':
          session_state['prevTab']['sub2'] = 'Trades'
  
          from ethan_coin.trades.trades import trades
          trades(userAccount)
          
        elif view == 'Make Trade':
          session_state['prevTab']['sub2'] = 'Make Trade'
  
          from ethan_coin.trades.make_trade import make_trade
          make_trade(userAccount)
        elif view == 'Manage':
          session_state['prevTab']['sub2'] = 'Manage'
  
          from ethan_coin.trades.manage import manage
          manage(userAccount)
      elif selected == 'Gamble':
        session_state['prevTab']['sub1'] = 'Gamble'
        session_state['loop'] = False
  
        st.header('Gamble')
        st.write('The key to success')
        st.write('---')
        elon = 'data:image/jpeg;base64,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'
        div = f"""
        <div class="chat-row">
            <img class="chat-icon" src="{elon}" width=128 height=128>
  
        </div>
        """
        st.markdown(div, unsafe_allow_html=True)
        st.write('*\"Most gamblers quit right before they hit big.\"* - Elon Musk')
  
        steve = 'https://m.media-amazon.com/images/I/71sVQDj0SCL._AC_UF1000,1000_QL80_.jpg'
  
        div = f"""
        <div class="chat-row">
            <img class="chat-icon" src="{steve}" width=128 height=128>
  
        </div>
        """
        st.markdown(div, unsafe_allow_html=True)
        st.write('*\"I don\'t believe in addiction, I only believe in dedication.\"* - Steve Jobs')
  
        mark = 'data:image/jpeg;base64,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'
  
        div = f"""
        <div class="chat-row">
            <img class="chat-icon" src="{mark}" width=128 height=128>
  
        </div>
        """
        st.markdown(div, unsafe_allow_html=True)
        st.write('*\"After dropping out of collage, all hope seemed lost. But gambling my remaining Ethan Coin lead to my success.\"* - Mark Zuckerberg')
  
        joe = 'data:image/jpeg;base64,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'
  
        div = f"""
        <div class="chat-row">
            <img class="chat-icon" src="{joe}" width=128 height=128>
  
        </div>
        """
        st.markdown(div, unsafe_allow_html=True)
  
        st.write('*\"The best way to get something done, if you- if you hold it near and dear to you and you uh... Um, like to be able to.. well anywase.\"* - Joe Biden')
        st.write('---')
        game = st.selectbox(label='Chosen Game', options=['Rock Paper Scissors', 'Flip a Coin', 'Blackjack'])
        amount=userCoinSum

        coin_img = get_display_image_src('local_data/files/EthanCoin/EthanCoin.png')

        div = f"""
        <div style="display: flex; align-items: center;">
            <img src="{coin_img}" width=192 height=192 style="margin-right: 10px;">
            <div style="display: flex; flex-direction: column;">
                <span style="font-size: 40px; font-weight: bold;">Ethan Coin Balance</span>
                <span style="font-size: 20px;">{str(userCoinSum)} EC</span>
            </div>
        </div>
        """

        st.markdown(div, unsafe_allow_html=True)
      
        st.write('')
        if userCoinSum == 0:
          st.error('You have no coins left. But keep tyring! never quit. You will one day hit big.')
        else:
          if game == 'Rock Paper Scissors':
            session_state['prevTab']['sub2'] = 'Rock Paper Scissors'
  
            from ethan_coin.gamble.rps import rps
            rps(userAccount, userCoinSum)
          elif game == 'Flip a Coin':
            session_state['prevTab']['sub2'] = 'Flip a Coin'
  
            from ethan_coin.gamble.flip_a_coin import flip_a_coin
            flip_a_coin(userAccount, userCoinSum)
          elif game == 'Blackjack':
            st.write('---')
            st.header('BlackJack')
            st.write('Coming Soon')
            
      elif selected == 'Marketplace':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Marketplace'
        st.header('Marketplace')
        st.write('Sell and Buy digital or physical things')
        st.write('---')
        view = st.selectbox(label='View', options=['Items', 'Sell', 'Manage'])
        if view == 'Items':
          session_state['prevTab']['sub2'] = 'Items'
  
          from ethan_coin.marketplace.items import items
          items(userAccount, userCoinSum)
        elif view == 'Sell':
          session_state['prevTab']['sub2'] = 'Sell'
  
          from ethan_coin.marketplace.sell import sell
          sell(userAccount, userCoinSum)
        elif view == 'Manage':
          session_state['prevTab']['sub2'] = 'Manage'
  
          from ethan_coin.marketplace.manage import manage
          manage(userAccount, userCoinSum)
          
      elif selected == 'Admin':
        session_state['loop'] = False
        session_state['prevTab']['sub1'] = 'Admin'
        if session_state['prevTab']['sub1'] != 'Admin':
          session_state['adminKey'] = None
  
        from ethan_coin.admin.admin import admin
        admin(userAccount)
