import streamlit as st
from streamlit_extras.stateful_button import button
from datetime import datetime

from local_services.local_db import Accounts, Articles, Submissions, Archives
from local_services.local_storage import (
  s3,
  bucket_name,
  get_display_image_src,
  local_path_to_key,
)


def accept(userAccount):
  st.header('Accept articles')
  st.write('use common sense')
  st.write('---')

  submissions = list(Submissions.find())

  if len(submissions) == 0:
    st.error('No submissions rn')
  else:
    if len(submissions) == 1:
      i = 1
    else:
      i = st.slider('Enter Index', min_value=1, max_value=len(submissions), value=1)

    submission = submissions[i-1]

    st.write('title: "'+submission['title']+'"')
    st.write('description: "'+submission['description']+'"')
    st.write('content: "'+submission['content']+'"')

    if submission.get('imagePath') != None:
      image_src = get_display_image_src(submission['imagePath'])
      div = f"""
        <div class="chat-row">
            <img class="chat-icon" src="{image_src}" width=128 height=128>
        </div>
        """
      st.markdown(div, unsafe_allow_html=True)
    else:
      st.write('No Image')

    submitterAccount = Accounts.find_one({'_id': submission['userid']})

    if submitterAccount != None:
      st.write('Submitter: '+submitterAccount['username'])
      st.write('userId: '+str(submitterAccount['_id']))
    else:
      st.warning('Submitter account not found')
      st.write('userId: '+str(submission['userid']))

    st.write('ArticleId: '+str(submission['_id']))

    accept_button = st.button(label='Accept')
    decline = button(label='Decline', key='decline-submission-button')

    if accept_button:
      Articles.insert_one(submission)

      Accounts.update_one(
        {'_id': submission['userid']},
        {
          '$push': {
            'inbox': {
              'msg': 'Your submission: "'+submission['title']+'", has been accepted for publication!',
              'type': 'Success',
              'time': datetime.utcnow().isoformat()
            }
          }
        }
      )

      Submissions.delete_one({'_id': submission['_id']})
      st.rerun()

    elif decline:
      decline_submission = st.form('decline-submission')

      with decline_submission:
        reason = st.text_input(label='Reason')
        press = st.form_submit_button(label='Submit')

        if press:
          Accounts.update_one(
            {'_id': submission['userid']},
            {
              '$push': {
                'inbox': {
                  'msg': 'Your submission: "'+submission['title']+'", has been declined for publication. Reason: '+reason+' Decliner: '+userAccount['username'],
                  'type': 'Error',
                  'time': datetime.utcnow().isoformat()
                }
              }
            }
          )

          if submission.get('imagePath') != None:
            s3.delete_object(
              Bucket=bucket_name,
              Key=local_path_to_key(submission['imagePath'])
            )

          Submissions.delete_one({'_id': submission['_id']})

          archived_submission = dict(submission)
          archived_submission['archiveType'] = 'declinedArticle'
          archived_submission['archivedId'] = archived_submission['_id']
          archived_submission['archiveDate'] = datetime.utcnow().isoformat()
          del archived_submission['_id']

          Archives.insert_one(archived_submission)
          st.rerun()
