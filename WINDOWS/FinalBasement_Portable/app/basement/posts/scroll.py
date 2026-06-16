import streamlit as st
import random
from datetime import datetime

from funcs import normalize_datetime
from local_services.local_db import Accounts, Posts
from local_services.local_storage import (
  s3,
  bucket_name,
  s3_url_to_local_path,
  local_path_to_key,
  get_display_image_src,
)


def normalize_id(value):
  if isinstance(value, dict) and '$oid' in value:
    return str(value['$oid'])
  return str(value)


def render_post_content(post):
  if post.get('content') == None:
    return

  content_type = post.get('contentType')
  content = post.get('content')

  if content_type == 'video':
    try:
      response = s3.get_object(
        Bucket=bucket_name,
        Key=local_path_to_key(content)
      )
      object_content = response['Body'].read()
      st.video(object_content)
    except Exception:
      st.video(s3_url_to_local_path(content))

  elif content_type == 'image':
    st.image(s3_url_to_local_path(content))

  else:
    st.video(content)
    st.write(content)


def scroll(userAccount):
  posts = list(Posts.find())

  if len(posts) == 0:
    st.header('No posts pls post ):')

  posts.reverse()

  for post in posts:
    st.subheader(post['title'])
    st.write(post['description'])

    postAccount = Accounts.find_one({'_id': post['userid']})

    if postAccount == None:
      post_username = 'Unknown'
      post_avatar = get_display_image_src('local_data/files/profile-images/guest.png')
    else:
      post_username = postAccount['username']
      post_avatar = get_display_image_src(postAccount['avatarPath'])

    render_post_content(post)

    post_date = normalize_datetime(post['date'])
    extra = ''

    if userAccount['status'] == 'Admin':
      extra = ' • Post ID '+str(post['_id'])

    div = f"""
          <div class="chat-row">
            <img class="chat-icon" src="{post_avatar}" width=32 height=32>
            {post_username+' | Likes '+str(len(post['likes']))+' • Dislikes '+str(len(post['dislikes']))+' • Comments '+str(len(post['comments']))+' • '+post_date.strftime('%B %dth, %Y')+extra}
            </div>
          </div>
        """

    st.markdown(div, unsafe_allow_html=True)
    st.write(' ')

    like = st.button(label='like', key=str(post['_id']))
    dislike = st.button(label='dislike', key=str(post['_id'])+'dislike')

    likes = post['likes']
    dislikes = post['dislikes']

    if like:
      unliked = False

      for i in likes:
        if normalize_id(i['_id']) == normalize_id(userAccount['_id']):
          Posts.update_one({'_id': post['_id']}, {'$pull': {'likes': {'_id': userAccount['_id']}}})
          unliked = True

      if unliked == False:
        for i in dislikes:
          if normalize_id(i['_id']) == normalize_id(userAccount['_id']):
            Posts.update_one({'_id': post['_id']}, {'$pull': {'dislikes': {'_id': userAccount['_id']}}})

        Posts.update_one({'_id': post['_id']}, {'$push': {'likes': {'_id': userAccount['_id']}}})

      st.rerun()

    if dislike:
      undisliked = False

      for i in dislikes:
        if normalize_id(i['_id']) == normalize_id(userAccount['_id']):
          Posts.update_one({'_id': post['_id']}, {'$pull': {'dislikes': {'_id': userAccount['_id']}}})
          undisliked = True

      if undisliked == False:
        for i in likes:
          if normalize_id(i['_id']) == normalize_id(userAccount['_id']):
            Posts.update_one({'_id': post['_id']}, {'$pull': {'likes': {'_id': userAccount['_id']}}})

        Posts.update_one({'_id': post['_id']}, {'$push': {'dislikes': {'_id': userAccount['_id']}}})

      st.rerun()

    comments = st.expander('Comments('+str(len(post['comments']))+')')

    with comments:
      if len(post['comments']) == 0:
        st.write('no comments')
      else:
        for comment in post['comments']:
          commentAccount = Accounts.find_one({'_id': comment['userid']})

          if commentAccount == None:
            comment_username = 'Unknown'
            comment_avatar = get_display_image_src('local_data/files/profile-images/guest.png')
          else:
            comment_username = commentAccount['username']
            comment_avatar = get_display_image_src(commentAccount['avatarPath'])

          extra = ''

          if userAccount['status'] == 'Admin':
            extra = ' ('+comment['_id']+')'

          div = f"""
                <div class="chat-row">
                  <img class="chat-icon" src="{comment_avatar}" width=32 height=32>
                   {comment_username+extra+': '+comment['text']}
                  </div>
                </div>
                """

          st.markdown(div, unsafe_allow_html=True)
          st.write(' ')

      key = str(post['_id'])+'comment'

      commentform = st.form(key)

      with commentform:
        text = st.text_input(label='Enter comment', max_chars=60)
        press = st.form_submit_button('Comment')

        if press:
          if text.strip() == '':
            st.error('Enter a comment')
          else:
            commentIds = [i['_id'] for i in post['comments']]

            while True:
              code = ''
              for i in range(5):
                code += str(random.randint(0,9))
              if code not in commentIds:
                break

            Posts.update_one(
              {'_id': post['_id']},
              {
                '$push': {
                  'comments': {
                    '_id': code,
                    'userid': userAccount['_id'],
                    'postId': post['_id'],
                    'text': text,
                    'date': datetime.utcnow().isoformat()
                  }
                }
              }
            )
            st.rerun()

    st.write('---')
