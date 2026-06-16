import streamlit as st
from datetime import datetime
import random
from pathlib import Path

from local_services.local_db import Submissions, Articles
from local_services.local_storage import s3, bucket_name, get_local_file_url


def normalize_id(value):
  if isinstance(value, dict) and '$oid' in value:
    return str(value['$oid'])
  return str(value)


def submit(userAccount):
  submissions = list(Submissions.find())
  allowed = True

  for i in submissions:
    if normalize_id(i['userid']) == normalize_id(userAccount['_id']):
      st.error('You have a article out for submission already cuzzo')
      allowed = False

  if allowed:
    submitform = st.form('submit-form')

    with submitform:
      st.header('Submit Article')
      st.write('hi')
      title = st.text_input(label='Article Title', max_chars=45)
      description = st.text_input(label='Article Description', max_chars=100)
      content = st.text_area(label='Article Content', max_chars=3000)
      image = st.file_uploader(label='Article Image', type=['jpg', 'png', 'jpeg'])

      submit_button = st.form_submit_button(label='Submit')

      if submit_button:
        st.write('Submitting...')

        image_url = None

        if image != None:
          response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix='article-images'
          )

          file_names = [obj['Key'] for obj in response.get('Contents', [])]

          while True:
            code = ''
            for i in range(5):
              code += str(random.randint(0,9))

            original_stem = Path(image.name).stem
            fileName = original_stem + '_' + code + '.png'
            s3_key = 'article-images/' + fileName

            if s3_key not in file_names:
              break

          image.seek(0)
          s3.upload_fileobj(image, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})
          image_url = get_local_file_url(s3_key)

        while True:
          code = ''
          for i in range(5):
            code += str(random.randint(0,9))

          existing_submission_ids = [i['_id'] for i in Submissions.find()]
          existing_article_ids = [i['_id'] for i in Articles.find()]

          if code not in existing_submission_ids and code not in existing_article_ids:
            break

        article = {
          '_id': code,
          'userid': userAccount['_id'],
          'title': title,
          'description': description,
          'content': content,
          'imagePath': image_url,
          'date': datetime.utcnow().isoformat()
        }

        Submissions.insert_one(article)
        st.markdown(
          'Submited!',
          help='You will have to wait to see if your article get accepted. Follow your inbox to get uptaded'
        )
