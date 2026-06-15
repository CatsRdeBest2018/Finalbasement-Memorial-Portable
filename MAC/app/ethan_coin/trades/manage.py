from datetime import datetime
import streamlit as st


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
def manage(userAccount):
  st.subheader('Manage')
  st.write('See your trades')
  trades = list(Trades.find({'userid': userAccount['_id']}))
  if len(trades) != 0:
    st.header('You have '+str(len(trades))+' trade(s) active:')
    st.write('---')
    for trade in trades:
      st.subheader(trade['text'])
      delete = st.button(label='Delete', key=str(trade['_id']))
      if delete:
        Trades.delete_one({'_id': trade['_id']})
        st.rerun()
      st.write('---')
  else:
    st.error('No active trades')