import streamlit as st
from streamlit import session_state
import time
from funcs import convertTime, openSession, normalize_datetime
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
  local_path_to_key,
)


def normalize_id(value):
  if isinstance(value, dict) and '$oid' in value:
    return str(value['$oid'])
  return str(value)


def same_id(a, b):
  return normalize_id(a) == normalize_id(b)


def delete_stored_file(path):
  if path == None:
    return

  if local_path_to_key(path) == 'profile-images/guest.png':
    return

  try:
    s3.delete_object(Bucket=bucket_name, Key=local_path_to_key(path))
  except Exception as e:
    st.warning(f'Could not delete local file: {e}')


def admin(userAccount):
  
  if session_state['adminKey'] == userAccount['password']:
    st.header('Welcome Master')
    st.write('What do you wish to do today 😩😩😩😩😩')
    st.write('---')

    adminSelect = st.selectbox(label='Pick', options=['Analytics', 'Account styff', 'Delete Thangs', 'Ghost View Chatrooms 😈😈😈', 'View Suggestions', 'Online', 'Archives'])


    st.write('---')
    if adminSelect == 'Analytics':
      st.write('not done yet')
    elif adminSelect == 'Delete Thangs':
      session_state['loop'] = True
      st.subheader('Delete things')
      deleteSelect = st.selectbox(label='Pick', options=['Accounts', 'Articles', 'Posts', 'Comments'])

      if deleteSelect == 'Accounts':

        accountdeleteform = st.form('account-delete-form')
        with accountdeleteform:
          username = st.text_input(label='Enter Username')
          delete = st.form_submit_button(label='Delete')

          if delete:
            account = Accounts.find_one({'username': username})
            if account == None:
              st.error('Account doesnt exist pluh')
            else:
              for acct in Accounts.find():
                for friend in acct['friends']:
                  if same_id(friend['_id'], account['_id']):
                    Accounts.update_one({'_id': acct['_id']}, {'$pull': {'friends': friend}})
                for friendRequest in acct['friendRequests']:
                  if same_id(friendRequest['_id'], account['_id']):
                    Accounts.update_one({'_id': acct['_id']}, {'$pull': {'friendRequests': friend}})
              for article in Articles.find():
                if same_id(article['userid'], account['_id']):
                  if article['imagePath'] != None:
                    delete_stored_file(article['imagePath'])
                  Articles.delete_one({'_id': article['_id']})
              for post in Posts.find():
                if same_id(post['userid'], account['_id']):
                  if post['contentType'] in ['video', 'image']:
                    delete_stored_file(post['content'])
                  Posts.delete_one({'_id': post['_id']})
                else:
                  for comment in post['comments']:
                    if same_id(comment['userid'], account['_id']):
                      Posts.update_one({'_id': post['_id']}, {'$pull': {'comments': comment}})
                  for like in post['likes']:
                    if same_id(like['_id'], account['_id']):
                      Posts.update_one({'_id': post['_id']}, {'$pull': {'likes': like}})
                  for dislike in post['dislikes']:
                    if same_id(dislike['_id'], account['_id']):
                      Posts.update_one({'_id': post['_id']}, {'$pull': {'dislikes': dislike}})
              for session in Sessions.find():
                for message in session['history']:
                  if same_id(message.get('userid'), account['_id']):
                    Sessions.update_one({'_id': session['_id']}, {'$pull': {'history': message}})
                for person in session['people']:
                  if same_id(person['_id'], account['_id']):
                    Sessions.update_one({'_id': session['_id']}, {'$pull': {'people': person}})
              for random in Randoms.find():
                if same_id(random['_id'], account['_id']):
                  Randoms.delete_one({'_id': random['_id']})
                  Sessions.delete_one({'_id': random['sessionId']})

              if account['avatarPath'] != get_local_file_url('profile-images/guest.png'):
                delete_stored_file(account['avatarPath'])
              Accounts.delete_one({'_id': account['_id']})

              st.error('Deleted')
              time.sleep(2)
              st.rerun()
      elif deleteSelect == 'Articles':
        articledeleteform = st.form('article-delete-form')
        with articledeleteform:
          id = st.text_input(label='Enter Article ID')
          delete = st.form_submit_button(label='Delete')

          if delete:
            article = Articles.find_one({'_id': id})
            if article == None:
              st.error('Article not found')
            else:
              if article['imagePath'] != None:          
                delete_stored_file(article['imagePath'])
              Articles.delete_one({'_id': id})
              st.error('Article Deleted')
              time.sleep(2)
              st.rerun()
      elif deleteSelect == 'Posts':
        postdeleteform = st.form('post-delete-form')
        with postdeleteform:
          id = st.text_input(label='Enter Post ID')
          delete = st.form_submit_button(label='Delete')

          if delete:
            post = Posts.find_one({'_id': id})
            if post == None:
              st.error('Post not found')
            else:
              if post['contentType'] in ['video', 'image']:
                delete_stored_file(post['content'])
              Posts.delete_one({'_id': post['_id']})
              st.error('Post Deleted')
              time.sleep(2)
              st.rerun()
      elif deleteSelect == 'Comments':
        commentdeleteform = st.form('comment-delete-form')
        with commentdeleteform:
          postId = st.text_input(label='Enter Post ID')
          commentId = st.text_input(label='Enter Comment ID')
          delete = st.form_submit_button(label='Delete')

          if delete:
            post = Posts.find_one({'_id': postId})
            if post == None:
              st.error('Post not found')
            else:
              found = False
              for comment in post['comments']:
                if comment['_id'] == commentId:
                  Posts.update_one({'_id': postId}, {'$pull': {'comments': comment}})
                  found = True
                  break
              if found == False:
                st.error('Comment not found')
    elif adminSelect == 'Account styff':
      st.subheader('Account stuff')
      accountStuffSelect = st.selectbox(label='Pick', options=['Edit Username', 'Edit Password', 'Remove Avatar', 'View Inbox'])
      if accountStuffSelect == 'Edit Username':
        editusernameform = st.form('edit-username-form')
        with editusernameform:
          username = st.text_input(label='Username')
          newUsername = st.text_input(label='New Username')
          edit = st.form_submit_button(label='edit')
          if edit:
            account = Accounts.find_one({'username': username})
            if account == None:
              st.error('Account not found')
            else:
              Accounts.update_one({'_id': account['_id']}, {'$set': {'username': newUsername}})
              st.success('Updated')
      elif accountStuffSelect == 'Edit Password':
        editpasswordameform = st.form('edit-password-form')
        with editpasswordameform:
          username = st.text_input(label='Username')
          newPassword = st.text_input(label='New Password')
          edit = st.form_submit_button(label='edit')
          if edit:
            account = Accounts.find_one({'username': username})
            if account == None:
              st.error('Account not found')
            else:
              Accounts.update_one({'_id': account['_id']}, {'$set': {'password': newPassword}})
              st.success('Updated')
      elif accountStuffSelect == 'Remove Avatar':
        removeavatarform = st.form('remove-avatar-form')
        with removeavatarform:
          username = st.text_input(label='Username')

          remove = st.form_submit_button(label='remove')
          if remove:
            account = Accounts.find_one({'username': username})
            if account == None:
              st.error('Account not found')
            else:
              Accounts.update_one({'_id': account['_id']}, {'$set': {'avatarPath': get_local_file_url('profile-images/guest.png')}})
              st.success('Updated')
      elif accountStuffSelect == 'View Inbox':
        viewinboxform = st.form('view-inbox-form')
        with viewinboxform:
          username = st.text_input(label='Username')

          view = st.form_submit_button(label='View')
          if view:
            account = Accounts.find_one({'username': username})
            if account == None:
              st.error('Account not found')
            else:
              inbox = account['inbox']
              inbox.reverse()
              for message in inbox:
                type = message['type']
                msg = message['msg']

                utc_offset = session_state['utcOffset']

                converted_time = convertTime(message['time'], utc_offset)
                formatted_datetime = converted_time.strftime("%B, %dth %I:%M %p")
                if type == 'Error':
                  st.error(msg+' - '+formatted_datetime)
                elif type  == 'Warning':
                  st.warning(msg+' - '+formatted_datetime)
                else:
                  st.success(msg+' - '+formatted_datetime)
    elif adminSelect == 'Ghost View Chatrooms 😈😈😈':
      st.header('Chatrooms')
      st.write('Make sure no one can see ur screen while using this')
      st.write('---')

      view = st.selectbox(label='Pick', options=['Ghost', 'View'])
      if view == 'Ghost':
        viewchatform = st.form('view-chat-form')
        theSession = None
        with viewchatform:
          id = st.text_input(label='Enter ID')
          press = st.form_submit_button(label='Enter')
          if press:
            theSession = Sessions.find_one({'_id': id})
            if theSession == None:
              st.error('Incorrect ID')

        if theSession != None:

          openSession(id, 'ghost')
      elif view == 'View':
        session_state['loop'] = True
        sessions = list(Sessions.find())
        if len(sessions) == 1:
          st.error('no sessions rn')

        for session in Sessions.find():
          if session['_id'] == 'OMEGA_CHAT' or session['isRandom']:
            continue

          st.write('Title: '+session['title'])
          st.write('Description: '+session['description'])
          st.write('Privacy: '+session['privacy'])
          peopleLst = []
          for person in session['people']:
            peopleLst.append(person['username'])
          st.write('Active People: '+', '.join(peopleLst))
          st.write('ID: '+session['_id'])
          st.write('---')
        st.button('reload')
    elif adminSelect == 'View Suggestions':
      st.header('view suggestions')
      st.write('---')
      suggestions = list(Suggestions.find())
      if len(suggestions) == 0:
        st.error('No suggestions rn')
      else:
        for suggestion in suggestions:
          account = Accounts.find_one({'_id': suggestion['userid']})

          st.subheader('By '+account['username']+':')
          st.write(suggestion['content'])
          accept = st.button(label='accept', key=suggestion['_id'])
          if accept:
            Suggestions.delete_one({'_id': suggestion['_id']})
            st.rerun()
          st.write('---')
    elif adminSelect == 'Archives':
      st.header('Archives')
      st.write('Im sorry you have to use this')
      st.write('---')
      archiveType = st.selectbox(label='Enter Archive Type', options=['View Archive', 
  'userSession', 'omegaInstance', 'editedUsername', 'editedAboutMe', 'declinedArticle', 'deletedPost', 'deletedComment', 'adminCoins'])
      if archiveType == 'View Archive':
        viewarchiveform = st.form('view-archive-form')
        with viewarchiveform:
          id = st.text_input(label='archiveId')

          view = st.form_submit_button(label='View')
          if view:
            archive = Archives.find_one({'_id': id})
            if archive == None:
              st.error('Not found')
            else:
              st.write(archive)
      elif archiveType == 'userSession':
        usersessionarchiveform = st.form('user-session-archive-form')
        with usersessionarchiveform:
          st.header('User Session query')
          st.write('leave any blank for no query')
          id = st.text_input(label='Session Id')
          title = st.text_input(label='Session Title')
          description = st.text_input(label='Session Description')
          message = st.text_input(label='Message Content')
          messageAccount = st.text_input(label='Message Username')

          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'userSession':
                continue

              if id != '':
                if archive['archivedId'] != id:
                  continue
              if title != '':
                if archive['title'] != title:
                  continue
              if description != '':
                if archive['description'] != description:
                  continue
              if message != '':
                found = False
                for archivedMessage in archive['history']:
                  if archivedMessage['text'] == message:
                    found = True
                    if messageAccount != '':
                      if archivedMessage['username'] != messageAccount:
                        found = False
                if found == False:
                  continue
              foundArchives.append(archive)

            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
      elif archiveType == 'omegaInstance':
        omegainstancearchiveform = st.form('omega-instance-archive-form')
        with omegainstancearchiveform:
          st.header('Omega Instance query')
          st.write('leave any blank for no query')
          message = st.text_input(label='Message Content')
          messageAccount = st.text_input(label='Message Username')

          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'omegaInstance':
                continue
              if message != '':
                found = False
                for archivedMessage in archive['history']:
                  if archivedMessage['text'] == message:
                    found = True
                    if messageAccount != '':
                      if archivedMessage['username'] != messageAccount:
                        found = False
                if found == False:
                  continue
              foundArchives.append(archive)

            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
      elif archiveType == 'editedUsername':
        editedusernamearchiveform = st.form('edited-username-archive-form')
        with editedusernamearchiveform:
          st.header('Edited Username query')
          st.write('leave any blank for no query')
          editedUsername = st.text_input(label='Edited Username')
          currentUsername = st.text_input(label='Current Username')
          userId = st.text_input(label='UserId')


          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'editedUsername':
                continue
              if editedUsername != '':
                if archive['username'] != editedUsername:
                  continue
              if currentUsername != '':
                if Accounts.find_one({'_id': archive['userid']})['username'] != currentUsername:
                  continue
              if userId != '':
                if not same_id(archive['userid'], userId):
                  continue
              foundArchives.append(archive)

            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
      elif archiveType == 'editedAboutMe':
        editedaboutmearchiveform = st.form('edited-about-me-archive-form')
        with editedaboutmearchiveform:
          st.header('Edited About Me query')
          st.write('leave any blank for no query')
          editedAboutMe = st.text_input(label='Edited About Me')
          currentUsername = st.text_input(label='Current Username')
          userId = st.text_input(label='UserId')


          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'editedAboutMe':
                continue
              if editedAboutMe != '':
                if archive['aboutMe'] != editedAboutMe:
                  continue
              if currentUsername != '':
                if Accounts.find_one({'_id': archive['userid']})['username'] != currentUsername:
                  continue
              if userId != '':
                if not same_id(archive['userid'], userId):
                  continue
              foundArchives.append(archive)

            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
      elif archiveType == 'declinedArticle':

        declinedarticlearchiveform = st.form('declined-article-archive-form')
        with declinedarticlearchiveform:

          st.header('Declined article query')
          st.write('leave any blank for no query')
          title = st.text_input(label='Article Title')
          description = st.text_input(label='Article Description')
          content = st.text_input(label='Content')
          userId = st.text_input(label='UserId')
          submissionId = st.text_input(label='Submission Id')
          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'declinedArticle':
                continue
              if title != '':
                if archive['title'] != title:
                  continue
              if description != '':
                if archive['description'] != description:
                  continue
              if content != '':
                if archive['content'] != content:
                  continue
              if userId != '':
                if not same_id(archive.get('userId'), userId):
                  continue
              if submissionId != '':
                if archive['archivedId'] != submissionId:
                  continue
              foundArchives.append(archive)

            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
      elif archiveType == 'deletedPost':
        deletedpostarchiveform = st.form('deleted-post-archive-form')
        with deletedpostarchiveform:

          st.header('Deleted Post query')
          st.write('leave any blank for no query')
          title = st.text_input(label='Post Title')
          description = st.text_input(label='Post Description')
          contentType = st.text_input(label='Content Type')
          currentUsername = st.text_input(label='Current Username')
          userId = st.text_input(label='UserId')
          postId = st.text_input(label='PostId')

          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'deletedPost':
                continue
              if title != '':
                if archive['title'] != title:
                  continue
              if description != '':
                if archive['description'] != description:
                  continue
              if contentType != '':
                if archive['contentType'] != contentType:
                  if archive['contentType'] == None:
                    if contentType != 'null':
                      continue
                  else:
                    continue
              if currentUsername != '':
                if Accounts.find_one({'_id': archive['userid']})['username'] != currentUsername:
                  continue
              if userId != '':
                if not same_id(archive['userid'], userId):
                  continue
              if postId != '':
                if not same_id(archive['archivedId'], postId):
                  continue
              foundArchives.append(archive)

            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
      elif archiveType == 'deletedComment':
        deletedcommentarchiveform = st.form('deleted-comment-archive-form')
        with deletedcommentarchiveform:

          st.header('Deleted Comment query')
          st.write('leave any blank for no query')
          text = st.text_input(label='Comment Text')
          postTitle = st.text_input(label='Post Title')
          postId = st.text_input(label='Post Id')
          currentUsername = st.text_input(label='Current Username')
          userId = st.text_input(label='UserId')
          commentId = st.text_input(label='Comment Id')
          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'deletedComment':
                continue
              if text != '':
                if archive['text'] != text:
                  continue
              if postTitle != '' or postId != '':
                post = Posts.find_one({'_id': archive['postId']})
                if post == None:
                  for postArchive in [archive for archive in Archives.find() if archive['archiveType'] == 'deletedPost']:
                    found = False
                    if postArchive['archivedId'] == archive['postId']:
                      found = True
                      thePostId = postArchive['archivedId']
                  if found == False:
                    continue
                  post = Posts.find_one({'_id': thePostId})
              if postTitle != '':
                if post['title'] != postTitle:
                  continue
              if postId != '':
                if not same_id(post['_id'], postId):
                  continue

              if currentUsername != '':
                if Accounts.find_one({'_id': archive['userid']})['username'] != currentUsername:
                  continue
              if userId != '':
                if not same_id(archive['userid'], userId):
                  continue
              if commentId != '':
                if archive['archivedId'] != commentId:
                  continue
              foundArchives.append(archive)
            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
      elif archiveType == 'adminCoins':
        admincoinsarchiveform = st.form('admin-coins-archive-form')
        with admincoinsarchiveform:
          st.header('Archive admin coins query')
          amount = st.text_input('enter amount')
          user = st.text_input('Enter username')
          query = st.form_submit_button(label='Query')
          if query:
            foundArchives = []
            for archive in Archives.find():
              if archive['archiveType'] != 'adminCoins':
                continue
              if amount != '':
                if str(len(archive['coins'])) != amount:
                  continue
              if user != '':
                if archive['username'] != user:
                  continue
              foundArchives.append(archive)

            st.write('Found '+str(len(foundArchives))+' archives')
            for archive in foundArchives:
              st.write(archive['_id'])
    elif adminSelect == 'Online':
      st.header('Online')
      st.write('See whos online')
      st.write('---')
      for account in Accounts.find():
        if account['active']['online']:
          st.subheader(account['username'])
          now = datetime.utcnow()
          st.write(str((now - normalize_datetime(account['active']['date'])).total_seconds())+' seconds')
      st.button('refresh')
  else:
    adminKey = st.text_input(label='Pasword', type='password')
    session_state['adminKey'] = adminKey
    if adminKey != '':
      st.rerun()