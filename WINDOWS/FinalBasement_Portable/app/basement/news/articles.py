import streamlit as st
from streamlit import session_state

from funcs import convertTime
from local_services.local_db import Accounts, Articles
from local_services.local_storage import get_display_image_src


def articles(userAccount):
  articles = list(Articles.find())

  if len(articles) == 0:
    st.write('No articles')
  else:
    articles.reverse()
    articles_by_date = {}

    for article in articles:
      utc_offset = session_state['utcOffset']
      converted_time = convertTime(article['date'], utc_offset)
      date = converted_time.strftime("%B, %dth %Y")

      if date not in articles_by_date:
        articles_by_date[date] = [article]
      else:
        articles_by_date[date].append(article)

    for date in articles_by_date:
      st.header(date)
      st.write('\----------')

      for article in articles_by_date[date]:
        publisher = Accounts.find_one({'_id': article['userid']})

        if publisher != None:
          publisher_name = publisher['username']
        else:
          publisher_name = 'Unknown'

        st.subheader(article['title']+', Publisher: '+publisher_name)

        if userAccount['status'] == 'Admin':
          st.write(article['_id'])

        st.write(article['description'])
        st.write('---')
        st.write(article['content'])

        if article.get('imagePath') != None:
          image_src = get_display_image_src(article['imagePath'])
          div = f"""
            <div class="chat-row">
                <img class="chat-icon" src="{image_src}" width=256 height=256>
            </div>
            """
          st.markdown(div, unsafe_allow_html=True)

        st.write('---')
