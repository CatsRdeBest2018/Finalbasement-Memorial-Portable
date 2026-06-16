import streamlit as st
import random
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
def sell(userAccount, userCoinSum):
  st.header('Sell')
  st.write('Sell something')
  title = st.text_input(label='Title')
  description = st.text_area(label='Description')
  thumbnail = st.file_uploader(label='Upload thumbnail (optional)', type=['mp4', 'mov', 'mkv', 'avi','png', 'jpg'], )
  type = st.radio(label='Is your item digital or pysical?', options=['Physical', 'Digital'])
  st.write('---')
  if type == 'Digital':
    st.subheader('Digital')
    text = st.text_area(label='Add text')
    vidimg = st.file_uploader(label='Video/Image', type=['mp4', 'mov', 'mkv', 'avi','png', 'jpg'])
    file = st.file_uploader(label='Add file')       
  else:
    st.subheader('Make sure to include details about your physical item in your title/description')
  st.write('---')
  privacyKey = st.text_input(label='Enter Privacy Key (Leave blank for public)')
  price = st.number_input(label='Price', min_value=0.001, step=0.001)
  submit = st.button(label='Submit')
  if submit:
    st.write('posting...')
    if title == '' or description == '':
      st.error('please provide a description/title')
    elif (type=='Digital') and (vidimg == None and text == '' and file == ''):
      st.error('Please provide at least one digital content')
    else:
      if privacyKey == '':
        privacyKey = None
      if type == 'Digital':
        if text == '':
          text = None
      videos = ['mp4', 'mov', 'mkv', 'avi']
      image = ['png', 'jpg']
      thumbnailLink = None
      thumbnailContentType = None
      digitalVidimgLink = None
      digitalVidimgType = None
      digitalFileLink = None

      for i in range(2):
        theFile = None
        if thumbnail != None and i == 0:
          print('here')
          theFile = thumbnail
        elif type == 'Digital' and i == 1:
          if vidimg != None:
            theFile = vidimg
      
        if theFile != None:
          try:
            response = s3.list_objects_v2(
              Bucket=bucket_name,
              Prefix='marketplace-files'
            )
          except Exception as e:
            st.write(e)
          file_names = [obj['Key'] for obj in response.get('Contents', [])]
          if theFile.name[-3:] not in videos:
            while True:
              code = ''
              for j in range(5):
                code+=str(random.randint(0,9))
              amount = 4      
              ending = '.png'
              fileName = str(theFile.name)[:-amount]+'_'+code+ending
              if fileName not in file_names:
                break
            s3_key = 'marketplace-files/'+fileName
            s3.upload_fileobj(theFile, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})
            if i == 0:
              thumbnailLink = get_local_file_url(s3_key)
              thumbnailContentType = 'image'
              print('here2')
            elif i == 1:
              digitalVidimgLink = get_local_file_url(s3_key)
              digitalVidimgType = 'image'

          else:
            theFile.seek(0)

            while True:
              code = ''
              for j in range(5):
                code+=str(random.randint(0,9))
              fileName = str(theFile.name)[:-4]+'_'+code+'.bin'
              if fileName not in file_names:
                break
            s3_key = 'marketplace-files/'+fileName
            s3.upload_fileobj(theFile, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})
            if i == 0:
              thumbnailLink = get_local_file_url(s3_key)
              thumbnailContentType = 'video'
            elif i == 1:
              digitalVidimgLink = get_local_file_url(s3_key)

              digitalVidimgType = 'video'
      if type == 'Digital':
        if file != None:
          response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix='marketplace-files'
          )
          file_names = [obj['Key'] for obj in response.get('Contents', [])]
          while True:
            code = ''
            for i in range(5):
              code+=str(random.randint(0,9))

            ending = ''
            for char in str(file.name)[::-1]:
              if char == '.':
                break
              ending+=char

            fileName = str(file.name).replace(' ', '_')+'_'+code
            if fileName not in file_names:
              break
          s3_key = 'marketplace-files/'+fileName

          s3.upload_fileobj(file, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})
          s3_keyTemp = 'marketplace-files/'+fileName
          s3_key = ''
          for char in s3_keyTemp:
            if char == ' ':
              s3_key+='+'
            else:
              s3_key+=char
          digitalFileLink = get_local_file_url(s3_key)

      if type == 'Digital':
        digital = {'text': text, 'contentType': digitalVidimgType, 'content': digitalVidimgLink, 'file': digitalFileLink}
      else:
        digital = None

      item = {'userid': userAccount['_id'], 'title': title, 'description': description, 'thumbnailType': thumbnailContentType, 'thumbnail': thumbnailLink, 'digital': digital, 'price': price, 'buyers': [], 'privacyKey': privacyKey, 'date': datetime.utcnow().isoformat()}
      Items.insert_one(item)
      st.write('Posted!')
