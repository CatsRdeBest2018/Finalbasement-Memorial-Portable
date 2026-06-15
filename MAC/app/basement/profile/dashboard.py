import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stateful_button import button
from datetime import datetime
from pathlib import Path
import time
from io import BytesIO
import random
from PIL import Image
from funcs import createAvatar

from local_services.local_db import Accounts, Archives
from local_services.local_storage import (
  s3,
  bucket_name,
  get_local_file_url,
  s3_url_to_local_path,
  local_path_to_key,
  get_display_image_src,
)


def dashboard(userAccount):
  avatar_path = get_display_image_src(userAccount['avatarPath'])

  div = f"""
        <div class="chat-row">
            <img class="chat-icon" src="{avatar_path}" width=192 height=192>
            <span style="font-size: 40px; font-weight: bold;">{'👋 Welcome, '+userAccount['username']}!</span>
        </div>
        """
  st.markdown(div, unsafe_allow_html=True)
  st.write('')
  colored_header(
    label="Account Information",
    color_name="violet-70",
    description=None
  )
  columns = st.columns(3)


  with columns[0]:
    st.subheader('Username:')
    st.write(userAccount['username'])
    edit_username = button(label='Edit Username', key='edit_username_button')
    if edit_username:
      new_username_container = st.empty()
      newusername = new_username_container.form('new_username_form')
      with newusername:
        new_username = st.text_input('Enter New Username', value=userAccount['username'])
        current_password = st.text_input('Enter Current Password', type='password')

        submit_placeholder = st.empty()
        press = submit_placeholder.form_submit_button('Submit')
        message = st.empty()

        if press == False:
          message.warning('Enter New Username and Current Password')
        if press:
          if current_password != userAccount['password']:
            message.error('Incorrect Password')
          else:
            allUsernames = [i['username'] for i in Accounts.find()]
            i=0
            for char in new_username:
              if char == ' ':
                if i == 1:
                  message.error('spaces cannot be next to eachother')
                  i=2
                  break
                else:
                  i=1
              else:
                i=0
            if i != 2:
              if len(new_username) > 20:
                message.error('Username must be under 20 characters')
              elif len(new_username) < 3:
                message.error('Username must be at least 3 characters long')
              elif new_username in allUsernames:
                message.error('Username taken lol')
              else:
                archiveUsername = {'username': userAccount['username'], 'userid': userAccount['_id'], 'archiveType': 'editedUsername', 'archiveDate': datetime.utcnow()}
                Archives.insert_one(archiveUsername)
                Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'username': new_username}})
                submit_placeholder.empty()
                i=3
                while True:
                  message.success('Username Updated! <'+str(i)+'>')
                  i-=1
                  if i < 0:
                    break
                  time.sleep(1)
                new_username_container.empty()

                st.rerun()

  with columns[1]:
    st.subheader('Password:')
    text = ''
    for i in range(len(userAccount['password'])):
      text+='\\*'
    st.write(text)
    edit_password = button(label='Edit Pasword', key='edit_password_button')
    if edit_password:
      edit_password_container = st.empty()
      newpassword = edit_password_container.form('new_password_form')

      with newpassword:
        new_password = st.text_input('Enter New Password', type='password')
        current_password = st.text_input('Enter Current Password', type='password')

        submit_placeholder = st.empty()
        press = submit_placeholder.form_submit_button(label='Submit')

        message = st.empty()
        if press != None:
          message.warning('Enter New Password and Current Password')
        if press:
          if current_password != userAccount['password']:
            message.error('Incorrect Password')
          else:
            if new_password == '':
              message.warning('Enter New Password and Current Password')
            else:
              Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'password': new_password}})
              submit_placeholder.empty()
              i=3
              while True:
                message.success('Password Updated! <'+str(i)+'>')
                i-=1
                if i < 0:
                  break
                time.sleep(1)
              edit_password_container.empty()
              st.rerun()

  with columns[2]:
    st.subheader('Avatar:')
    file_path = s3_url_to_local_path(userAccount['avatarPath'])
    local_path = Path(file_path)

    if local_path.exists():
      file_size = local_path.stat().st_size / 1000000
      unit = 'MB'
      if file_size < 1:
        file_size = round(file_size * 1000)
        unit = 'KB'
      else:
        file_size = round(file_size, 2)
      st.write(str(file_size)+' '+unit)
    else:
      st.write('File size unavailable')

    edit_avatar = button(label='Edit Avatar', key='edit_avatar_button')
    edit_avatar_container = st.empty()
    if edit_avatar:
      edit_avatar_container = st.empty()
      newavatar = edit_avatar_container.form('new_avatar_form')
      with newavatar:
        newPfp = st.file_uploader('Upload New Profile Picture', type=['jpg', 'png'])

        submit_placeholder = st.empty()
        press = submit_placeholder.form_submit_button(label='Submit')
        message = st.empty()

        if press == False:
          message.warning('Upload a new Profile')
        if press:
          if newPfp != None:
            bytes_data = newPfp.read()
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

              if local_path_to_key(userAccount['avatarPath']) != 'profile-images/guest.png':
                s3.delete_object(
                  Bucket=bucket_name,
                  Key=local_path_to_key(userAccount['avatarPath'])
                )

              s3.upload_fileobj(temp_buffer, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})

            image_url = get_local_file_url(s3_key)
            Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'avatarPath': image_url}})
            i=3
            while True:
              message.success('Avatar Updated! <'+str(i)+'>')
              i-=1
              if i < 0:
                break
              time.sleep(1)
            edit_avatar_container.empty()
            st.rerun()
          else:
            message.error('Please upload an image')


  st.write('---')

  st.header('About Me')
  userAboutMe = userAccount['aboutMe']
  if userAboutMe == None:
    header = 'Add About Me'
    st.write('You don\'t have an about me')
    initialPress = True
  else:
    st.markdown(userAboutMe)
    header='Edit About Me'
    initialPress = button(label='Edit About Me', key='add_aboutme_button')

  if initialPress:
    edit_aboutme_container = st.empty()
    editaboutme = edit_aboutme_container.form('edit_aboutme_form')
    with editaboutme:
      st.subheader(header)
      new_aboutme = st.text_area(label='Enter Text', value=userAboutMe)

      submit_placeholder = st.empty()
      press = submit_placeholder.form_submit_button(label='Submit')
      message = st.empty()

      if press == False or new_aboutme == '':
        message.warning('Enter About Me')
      if press and new_aboutme != '':
        lines = len(new_aboutme.split('\n'))
        if lines > 20:
          message.error('About Me must be lower then 20 lines')
        else:
          if userAccount['aboutMe'] != None:
            archiveAboutMe = {'aboutMe': userAccount['aboutMe'], 'userid': userAccount['_id'], 'archiveType': 'editedAboutMe', 'archiveDate': datetime.utcnow()}
            Archives.insert_one(archiveAboutMe)
          Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'aboutMe': new_aboutme}})
          submit_placeholder.empty()

          i=3
          while True:
            message.success('About Me Updated! <'+str(i)+'>')
            i-=1
            if i < 0:
              break
            time.sleep(1)
          edit_aboutme_container.empty()
          initialPress = False
          st.rerun()
