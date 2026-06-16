import streamlit as st
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
def manage(userAccount, userCoinSum):
  st.header('Manage Items')
  st.write('manage')
  st.write('---')
  items = []
  for item in Items.find():
    if same_id(item['userid'], userAccount['_id']):
      items.append(item)
  items.reverse()
  if len(items) > 1:
    i = st.slider(label='Latest-Oldest', min_value=1, max_value=len(items), value=1)
  elif len(items) == 1:
    i = 1
  if len(items) != 0:
    item = items[i-1]
    st.subheader(item['title'])
    st.write(item['description'])
    itemAccount = Accounts.find_one({'_id': item['userid']})
    if item['thumbnail'] != None:
      if item['thumbnailType'] == 'video':
        render_media(item['thumbnail'], 'video')
      elif item['thumbnailType'] == 'image':
        st.image(s3_url_to_local_path(item['thumbnail']))

    itemDate = normalize_datetime(item['date'])
    extra = ' • Item ID '+str(item['_id'])
    if item['digital'] == None:
      type = 'PHYSICAL'
    else:
      type = 'DIGITAL'

    div = f"""
          <div class="chat-row">
            <img class="chat-icon" src=\"{get_display_image_src(itemAccount['avatarPath'])}\" width=32 height=32>
            {itemAccount['username']+' • Sold '+str(len(item['buyers']))+' Times • '+type+' • '+normalize_datetime(item['date']).strftime('%B %dth, %Y')+extra}
            </div>
          </div>
          """

    st.markdown(div, unsafe_allow_html=True)
    st.write(' ')

    if item['digital'] != None:
      digitalItemsDropdown = st.expander(label='Digital Items')
      with digitalItemsDropdown:
        if item['digital']['text'] != None:
          st.subheader(item['digital']['text'])
        else:
          st.subheader('No text')
        st.write('---')
        if item['digital']['content'] != None:

          if item['digital']['contentType'] == 'video':
            render_media(item['digital']['content'], 'video')
          elif item['digital']['contentType'] == 'image':
            st.image(s3_url_to_local_path(item['digital']['content']))
          st.write('---')
        if item['digital']['file'] != None:
          st.subheader('One available file')
          st.write(item['digital']['file'])
    buyersDisplay = st.expander(label=str(len(item['buyers']))+' Buyers')
    with buyersDisplay:
      for buyer in item['buyers']:
        buyerAccount = Accounts.find_one({'_id': buyer['_id']})
        div = f"""
              <div class="chat-row">
                <img class="chat-icon" src=\"{get_display_image_src(buyerAccount['avatarPath'])}\" width=32 height=32>
                {buyerAccount['username']}
                </div>
              </div>
              """
        st.markdown(div, unsafe_allow_html=True)
        st.write('')
    delete = st.button(label='Delete \"'+item['title']+'\"')
    if delete:
      if item['thumbnail'] != None:
        delete_stored_file(item['thumbnail'])
      if item['digital'] != None:
        if item['digital']['content'] != None:
          delete_stored_file(item['digital']['content'])
        if item['digital']['file'] != None:
          delete_stored_file(item['digital']['file'])
      Items.delete_one({'_id': item['_id']})
      archive = dict(item)
      archive['archiveType'] = 'deletedItem'
      archive['archivedId'] = item['_id']
      archive['archiveDate'] = datetime.utcnow()
      del archive['_id']
      Archives.insert_one(archive)
      st.rerun()                                    
    st.write('---')
    editmarketplaceitemform = st.form('edit-marketplace-item-form')
    with editmarketplaceitemform:
      st.header('Edit item')
      st.write('edit this item')
      title = st.text_input('Edit Title', value=item['title'])
      description = st.text_input('Edit description', value=item['description'])
      price = st.number_input(label='Edit price', value=item['price'])
      edit = st.form_submit_button(label='Edit')
      if edit:
        Items.update_one({'_id': item['_id']}, {'$set': {'title': title, 'description': description, 'price': price}})
        archive = dict(item)
        archive['archiveType'] = 'editedItem'
        archive['archivedId'] = item['_id']
        archive['archiveDate'] = datetime.utcnow()
        del archive['_id']
        Archives.insert_one(archive)