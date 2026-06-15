import streamlit as st
import random
from datetime import datetime
from pathlib import Path

from funcs import normalize_datetime
from local_services.local_db import Posts
from local_services.local_storage import s3, bucket_name, get_local_file_url


def normalize_id(value):
  if isinstance(value, dict) and '$oid' in value:
    return str(value['$oid'])
  return str(value)


def post(userAccount):
  allowed = True

  for existing_post in reversed(list(Posts.find())):
    if normalize_id(existing_post['userid']) == normalize_id(userAccount['_id']):
      now = datetime.utcnow()
      post_date = normalize_datetime(existing_post['date'])

      if (now - post_date).total_seconds() <= 21600:
        st.error('Post every 6 hours')
        allowed = False
        break

  if allowed:
    postform = st.form('post-form')

    with postform:
      st.header('Post')
      st.write('pluh')
      title = st.text_input(label='Title', max_chars=40)
      description = st.text_input(label='Description', max_chars=100)

      file = st.file_uploader(
        label='Content',
        type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'mkv', 'avi']
      )

      ytLink = st.text_input(label='Youtube Link', max_chars=90)

      submit = st.form_submit_button(label='Post')

      videos = ['mp4', 'mov', 'mkv', 'avi']

      if submit:
        st.write('posting...')

        if title == '' or description == '':
          st.error('please provide a description/title')
        else:
          content = None
          contentType = None

          if file != None:
            response = s3.list_objects_v2(
              Bucket=bucket_name,
              Prefix='post-content'
            )
            file_names = [obj['Key'] for obj in response.get('Contents', [])]

            file_extension = Path(file.name).suffix.lower().lstrip('.')
            original_stem = Path(file.name).stem

            if file_extension not in videos:
              while True:
                code = ''
                for i in range(5):
                  code += str(random.randint(0,9))

                fileName = original_stem + '_' + code + '.png'
                s3_key = 'post-content/' + fileName

                if s3_key not in file_names:
                  break

              file.seek(0)
              s3.upload_fileobj(file, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})
              content = get_local_file_url(s3_key)
              contentType = 'image'

            else:
              while True:
                code = ''
                for i in range(5):
                  code += str(random.randint(0,9))

                # Keep original video extension instead of saving as .bin.
                fileName = original_stem + '_' + code + '.' + file_extension
                s3_key = 'post-content/' + fileName

                if s3_key not in file_names:
                  break

              file.seek(0)
              s3.upload_fileobj(file, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})
              content = get_local_file_url(s3_key)
              contentType = 'video'

          elif ytLink != '':
            content = ytLink
            contentType = 'yt'

          new_post = {
            'userid': userAccount['_id'],
            'title': title,
            'description': description,
            'contentType': contentType,
            'content': content,
            'comments': [],
            'likes': [],
            'dislikes': [],
            'date': datetime.utcnow().isoformat()
          }

          Posts.insert_one(new_post)
          st.write('Posted!')
