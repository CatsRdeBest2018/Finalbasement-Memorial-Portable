import streamlit as st
from datetime import datetime

from local_services.local_db import Posts, Archives
from local_services.local_storage import (
  s3,
  bucket_name,
  s3_url_to_local_path,
  local_path_to_key,
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


def manage(userAccount):
  st.subheader('Manage')
  st.write('delete stuff ig')
  st.write('---')

  posts = [
    post for post in Posts.find()
    if normalize_id(post['userid']) == normalize_id(userAccount['_id'])
  ]

  posts.reverse()
  st.subheader('You have '+ str(len(posts))+' posts rn')

  if len(posts) > 1:
    i = st.slider(label='Latest-Oldest', min_value=1, max_value=len(posts), value=1)
  elif len(posts) == 1:
    i = 1

  if len(posts) != 0:
    post = posts[i-1]

    st.subheader(post['title'])
    st.write(post['description'])

    render_post_content(post)

    st.write(
      'likes: '+str(len(post['likes'])),
      'dislikes: '+str(len(post['dislikes'])),
      'comments: '+str(len(post['comments'])),
      'post id: '+str(post['_id'])
    )

    deletePost = st.button(label='Delete "'+post['title']+'"')

    if deletePost:
      if post.get('content') != None:
        if post.get('contentType') != 'yt':
          s3.delete_object(
            Bucket=bucket_name,
            Key=local_path_to_key(post['content'])
          )

      Posts.delete_one({'_id': post['_id']})

      archived_post = dict(post)
      archived_post['archiveType'] = 'deletedPost'
      archived_post['archivedId'] = archived_post['_id']
      archived_post['archiveDate'] = datetime.utcnow().isoformat()
      del archived_post['_id']
      Archives.insert_one(archived_post)

      for comment in post['comments']:
        archived_comment = dict(comment)
        archived_comment['archiveType'] = 'deletedComment'
        archived_comment['archivedId'] = archived_comment['_id']
        archived_comment['archiveDate'] = datetime.utcnow().isoformat()
        del archived_comment['_id']
        Archives.insert_one(archived_comment)

      st.rerun()

  st.write('---')

  allComments = [comment for post in Posts.find() for comment in post['comments']]
  comments = []

  for comment in allComments:
    if normalize_id(comment['userid']) == normalize_id(userAccount['_id']):
      comments.append(comment)

  comments.reverse()
  st.subheader('You have '+str(len(comments))+ ' comments rn pluh')

  if len(comments) > 1:
    i = st.slider(label='Latest-Oldest', min_value=1, max_value=len(comments), value=1)
  elif len(comments) == 1:
    i = 1

  if len(comments) != 0:
    comment = comments[i-1]
    post = Posts.find_one({'_id': comment['postId']})

    if post == None:
      st.warning('Original post not found')
      return

    st.write('" '+comment['text']+' " on post: '+post['title'])
    st.write('commentId: '+comment['_id'], 'postId: '+str(post['_id']))

    deleteComment = st.button(label='delete "'+comment['text']+'"')

    if deleteComment:
      Posts.update_one({'_id': post['_id']}, {'$pull': {'comments': comment}})

      archived_comment = dict(comment)
      archived_comment['archiveType'] = 'deletedComment'
      archived_comment['archivedId'] = archived_comment['_id']
      archived_comment['archiveDate'] = datetime.utcnow().isoformat()
      del archived_comment['_id']
      Archives.insert_one(archived_comment)

      st.rerun()
