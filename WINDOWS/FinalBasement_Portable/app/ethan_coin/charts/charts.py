import streamlit as st
from streamlit import session_state
from datetime import datetime, timedelta
from funcs import convertTime
import plotly.express as px
import pandas as pd
from funcs import sumBal

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
def charts(userAccount):
  st.header('Charts')
  st.write('Break out the matrix')
  st.write('---')
  sum = 0.0
  for coin in EthanCoin.find():
    sum = round(sum+coin['value'],3)
  for coin in Lottery.find():
    sum = round(sum+coin['value'],3)

  st.subheader(str(sum)+'/1000 EC Mined!')
  st.write(str((sum/1000)*100)+'%')

  days = []
  sums = []
  archives = list(Archives.find())
  now = datetime.utcnow()
  converted_now = convertTime(now, session_state['utcOffset'])-timedelta(minutes=2)

  seven_days_ago = converted_now-timedelta(days=7)
  archived_coin_sums = [entry for entry in archives if (entry['archiveType'] == 'coinSum')and(convertTime(entry['archiveDate'], session_state['utcOffset'])-timedelta(minutes=2)) < seven_days_ago]
  for archive in archived_coin_sums:

    utc_offset = session_state['utcOffset']
    converted_archvive_time = convertTime(archive['archiveDate'], utc_offset)-timedelta(minutes=2)

    days.append(converted_archvive_time.strftime('%A'))
    sums.append(archive['amount'])

  days.append(converted_now.strftime('%A')+' (Today)')
  sums.append(sum)
  data = {'days': days, 'sums': sums}
  df = pd.DataFrame(data=data)

  fig = px.line(df, x='days', y='sums', title='Sums of EC')
  st.plotly_chart(fig)

  days = []
  values = []
  archives = list(Archives.find())

  archived_coin_values = [entry for entry in archives if (entry['archiveType'] == 'coinValueDay')and(convertTime(entry['archiveDate'], session_state['utcOffset'])-timedelta(minutes=2)) <= seven_days_ago]
  for archive in archived_coin_values:

    utc_offset = session_state['utcOffset']
    converted_archvive_time = convertTime(archive['archiveDate'], utc_offset)-timedelta(minutes=2)

    days.append(converted_archvive_time.strftime('%A'))
    values.append(archive['value'])
  days.append(converted_now.strftime('%A')+' (Today)')
  total = 0.0
  count = 0
  for archive in Archives.find():
    if archive['archiveType'] != 'coinValue':
      continue
    else:
      total = round(total+archive['value'],3)
      count+=1

  values.append(round(total/count,3) if count else 0)
  data = {'Days': days, 'Worth USD': values}
  df = pd.DataFrame(data=data)

  fig = px.line(df, x='Days', y='Worth USD', title='Worths of EC')
  st.plotly_chart(fig)
  st.warning('40% circulation breached, 1 USD is now 5 EC')
  st.write('---')
  st.subheader('LeaderBoard')
  st.write('here is leaderboard')
  st.warning('Loading...')
  allAccounts = filtered_list = [d for d in list(Accounts.find()) if d.get('onLeaderboard', False)]

  accountSums = [sumBal(account) for account in allAccounts]
  n = len(accountSums)
  for i in range(n):
    min_index = i
    for j in range(i + 1, n):
      if accountSums[j] > accountSums[min_index]:
        min_index = j
    accountSums[i], accountSums[min_index] = accountSums[min_index], accountSums[i]
    allAccounts[i], allAccounts[min_index] = allAccounts[min_index], allAccounts[i]

  places = {1: 'st', 2: 'nd', 3: 'rd'}

  for i in range(len(allAccounts)):
    account = allAccounts[i]
    accountSum = accountSums[i]
    if i+1 > 3:
      placement = 'th'
    else:
      placement = places[i+1]

    div = f'''
          <div style="display: flex; align-items: center;">
              <img src=\"{get_display_image_src(account['avatarPath'])}\" width=32 height=32 style="margin-right: 10px;">
              <div style="display: flex; flex-direction: column;">
                  <span style="font-size: 20px; font-weight: bold;">{str(i+1)+placement+': '}{account['username']}</span>
                  <span style="font-size: 15px;">{accountSum} EC</span>
              </div>
          </div>
          '''
    st.markdown(div, unsafe_allow_html=True, help='This person owns '+str((accountSum/1000)*100)+'% of circulation')
  st.write('---')
  if userAccount['onLeaderboard']:
    leave = st.button('Leave leaderboard')
    if leave:
      Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'onLeaderboard': False}})
      st.rerun()
  else:
    join = st.button('Join Leaderboard')
    if join:
      Accounts.update_one({'_id': userAccount['_id']}, {'$set': {'onLeaderboard': True}})
      st.rerun()
