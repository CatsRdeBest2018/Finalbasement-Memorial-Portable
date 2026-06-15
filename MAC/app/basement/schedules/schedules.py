import streamlit as st
from streamlit import session_state
from datetime import datetime, time as datetime_time
import pytz

from local_services.local_db import Accounts, Schedules

def schedules(userAccount):
  userSchedule = Schedules.find_one({'_id': userAccount['_id']})
  if userSchedule != None:
    st.header('Schedules')
    st.write('look at what people have')
    st.write('---')
    timezone_name = 'US/Eastern'
    current_time = datetime.now(pytz.timezone(timezone_name)).date()
    
    if current_time.strftime('%A') == 'Saturday' or current_time.strftime('%A') == 'Sunday': 
      st.header('its the weekend stupid pluh')
    else:
      actualDay = Schedules.find_one({'_id': 'CURRENT_DAY'})['day']
      ref = st.button(label='Refresh')
      st.write('---')
      if ref:
        if 'scheduleView' in session_state:
          del session_state['scheduleView']
          st.rerun()
      nextDay = st.button(label='Next Day')
      prevDay = st.button(label='Previous Day')
      nextPeriod = st.button(label='Next Period')
      prevPeriod = st.button(label='Previous Period')
      st.write('---')
      if nextDay:
        val = 1
        if actualDay+session_state['scheduleView']['dayOffset'] == 8:
          val = -7
        session_state['scheduleView']['dayOffset'] += val
      if prevDay:
        val = 1
        if actualDay+session_state['scheduleView']['dayOffset'] == 1:
          val = -7
        session_state['scheduleView']['dayOffset'] -= val
      if nextPeriod:
        val = 1
        if session_state['scheduleView']['period']+session_state['scheduleView']['periodOffset'] == 6:
          val = -6
        session_state['scheduleView']['periodOffset'] += val
      if prevPeriod:
        val = 1
        if session_state['scheduleView']['period']+session_state['scheduleView']['periodOffset'] == 0:
          val = -6
        session_state['scheduleView']['periodOffset'] -= val
      def getCurrentTime():
        current_time = datetime.now(pytz.timezone(timezone_name)).time()
        start_time = datetime_time(7, 30)
        end_time = datetime_time(15, 15)

        if not start_time <= current_time <= end_time:
          st.header('No school rn u goober')
          return 'no school'

        start_time = datetime_time(7, 30)
        end_time = datetime_time(8, 15)
        if start_time <= current_time <= end_time:
          st.header('Homeroom')
          return 'homeroom'

        start_time = datetime_time(9, 55)
        end_time = datetime_time(10, 20)
        if start_time <= current_time <= end_time:
          st.header('Recess')
          return 'recess'

        start_time = datetime_time(12, 0)
        end_time = datetime_time(12, 40)
        if start_time <= current_time <= end_time:
          st.header('Lunch tiem')
          return 'lunch'

        start_time = datetime_time(8, 15)
        end_time = datetime_time(9, 5)

        if start_time <= current_time <= end_time:
          return 0

        start_time = datetime_time(9, 5)
        end_time = datetime_time(9, 55)

        if start_time <= current_time <= end_time:
          return 1

        start_time = datetime_time(10, 20)
        end_time = datetime_time(11, 10)

        if start_time <= current_time <= end_time:
          return 2

        start_time = datetime_time(11, 10)
        end_time = datetime_time(12, 0)

        if start_time <= current_time <= end_time:
          return 3

        start_time = datetime_time(12, 40)
        end_time = datetime_time(13, 30)

        if start_time <= current_time <= end_time:
          return 4

        start_time = datetime_time(13, 30)
        end_time = datetime_time(14, 20)

        if start_time <= current_time <= end_time:
          return 5

        start_time = datetime_time(14, 10)
        end_time = datetime_time(15, 15)

        if start_time <= current_time <= end_time:
          return 6

      periodCalc = getCurrentTime()
      if periodCalc != 'no school':
        starting=''
        if periodCalc == 'homeroom':
          starting = 'Up Next: '
          periodCalc = 0
        elif periodCalc == 'recess':
          starting = 'Up Next: '
          periodCalc = 2
        elif periodCalc == 'lunch':
          starting = 'Up Next: '
          periodCalc = 4
        if 'scheduleView' not in session_state:
          session_state['scheduleView'] = {'dayOffset': 0, 'period': periodCalc, 'periodOffset': 0}
        
        currentDay = str(Schedules.find_one({'_id': 'CURRENT_DAY'})['day']+session_state['scheduleView']['dayOffset'])
        period = periodCalc+session_state['scheduleView']['periodOffset']
      

        st.header('Day '+currentDay+', '+current_time.strftime('%A')+', Period: '+str(period+1))
        st.subheader('My Schedule')
        mySchedule = st.expander(label=userAccount['username'])
        with mySchedule:
          st.subheader(starting+userSchedule[currentDay][period]['className'])
          if userSchedule[currentDay][period]['classNumber'] != None and userSchedule[currentDay][period]['classNumber'] != '':
            st.write('At: '+userSchedule[currentDay][period]['classNumber'])

          if period != 6:
            st.write('Up Next: '+userSchedule[currentDay][period+1]['className']+', At: '+str(userSchedule[currentDay][period+1]['classNumber']))
        st.write('---')
        for schedule in Schedules.find():
          if schedule['_id'] != 'CURRENT_DAY' and schedule['_id'] != userAccount['_id']:
            userSchedule = st.expander(label=Accounts.find_one({'_id': schedule['_id']})['username'])
            with userSchedule:
              st.subheader(starting+schedule[currentDay][period]['className'])
              classNumber = schedule[currentDay][period]['classNumber']
              if classNumber != None and classNumber != '':
                st.write('At: '+classNumber)
              if period != 6:
                st.write('Up Next: '+schedule[currentDay][period+1]['className']+', At: '+str(schedule[currentDay][period+1]['classNumber']))
            st.write('---')

  else:
    st.header('Create a Schedule')
    st.write('To start viewing other schedules please upload your own')
    st.write('---')

    allClasses = ['Science', 'History', 'English', 'Spanish', 'Spanish Adv', 'Chineese', 'French', 'Language', 'Math', 'Honors Math', 'Aerie Math', 'Art', 'Theater', 'Music', 'WHLS', 'Cityside', 'Other']
    roomNumbers = ['206', '213', '309', '113', '', '', '', '', '', '313', '', '404', 'Whe. WH', 'Gil. GCAB07', '', 'cityside', '']

    st.subheader('DAY 1')
    dayOneFirstClass = allClasses.index(st.selectbox(label='Day 1, First Class', options=allClasses))
    if allClasses[dayOneFirstClass] == 'Other':
      dayOneFirstClass = st.text_input(label='11Enter Class Name')
      dayOneFirstClassNumber = st.text_input(label='11Enter Room Number: ')
    elif roomNumbers[dayOneFirstClass] == '':
      dayOneFirstClassNumber = st.text_input(label='11Enter Room Number: ')
    elif roomNumbers[dayOneFirstClass] == 'cityside':
      dayOneFirstClassNumber = st.selectbox(label='11Choose', options=['in school', 'outside school'])
    else:
      dayOneFirstClassNumber = roomNumbers[dayOneFirstClass]

    dayOneSecondClass = allClasses.index(st.selectbox(label='Day 1, Second Class', options=allClasses))
    if allClasses[dayOneSecondClass] == 'Other':
      dayOneSecondClass = st.text_input(label='12Enter Class Name')
      dayOneSecondClassNumber = st.text_input(label='12Enter Room Number: ')
    elif roomNumbers[dayOneSecondClass] == '':
      dayOneSecondClassNumber = st.text_input(label='12Enter Room Number: ')
    elif roomNumbers[dayOneSecondClass] == 'cityside':
      dayOneSecondClassNumber = st.selectbox(label='12Choose', options=['in school', 'outside school'])
    else:
      dayOneSecondClassNumber = roomNumbers[dayOneSecondClass]

    dayOneThirdClass = allClasses.index(st.selectbox(label='Day 1, Third Class', options=allClasses))
    if allClasses[dayOneThirdClass] == 'Other':
      dayOneThirdClass = st.text_input(label='13Enter Class Name')
      dayOneThirdClassNumber = st.text_input(label='13Enter Room Number: ')
    elif roomNumbers[dayOneThirdClass] == '':
      dayOneThirdClassNumber = st.text_input(label='13Enter Room Number: ')
    elif roomNumbers[dayOneThirdClass] == 'cityside':
      dayOneThirdClassNumber = st.selectbox(label='13Choose', options=['in school', 'outside school'])
    else:
      dayOneThirdClassNumber = roomNumbers[dayOneThirdClass]

    dayOneFourthClass = allClasses.index(st.selectbox(label='Day 1, Fourth Class', options=allClasses))
    if allClasses[dayOneFourthClass] == 'Other':
      dayOneFourthClass = st.text_input(label='14Enter Class Name')
      dayOneFourthClassNumber = st.text_input(label='14Enter Room Number: ')
    elif roomNumbers[dayOneFourthClass] == '':
      dayOneFourthClassNumber = st.text_input(label='14Enter Room Number: ')
    elif roomNumbers[dayOneFourthClass] == 'cityside':
      dayOneFourthClassNumber = st.selectbox(label='14Choose', options=['in school', 'outside school'])
    else:
      dayOneFourthClassNumber = roomNumbers[dayOneFourthClass]

    dayOneFifthClass = allClasses.index(st.selectbox(label='Day 1, Fifth Class', options=allClasses))
    if allClasses[dayOneFifthClass] == 'Other':
      dayOneFifthClass = st.text_input(label='15Enter Class Name')
      dayOneFifthClassNumber = st.text_input(label='15Enter Room Number: ')
    elif roomNumbers[dayOneFifthClass] == '':
      dayOneFifthClassNumber = st.text_input(label='15Enter Room Number: ')
    elif roomNumbers[dayOneFifthClass] == 'cityside':
      dayOneFifthClassNumber = st.selectbox(label='15Choose', options=['in school', 'outside school'])
    else:
      dayOneFifthClassNumber = roomNumbers[dayOneFifthClass]

    dayOneSixthClass = allClasses.index(st.selectbox(label='Day 1, Sixth Class', options=allClasses))
    if allClasses[dayOneSixthClass] == 'Other':
      dayOneSixthClass = st.text_input(label='16Enter Class Name')
      dayOneSixthClassNumber = st.text_input(label='16Enter Room Number: ')
    elif roomNumbers[dayOneSixthClass] == '':
      dayOneSixthClassNumber = st.text_input(label='16Enter Room Number: ')
    elif roomNumbers[dayOneSixthClass] == 'cityside':
      dayOneSixthClassNumber = st.selectbox(label='16Choose', options=['in school', 'outside school'])
    else:
      dayOneSixthClassNumber = roomNumbers[dayOneSixthClass]

    dayOneElective = st.text_input(label='Enter Elective Period for Day 1')
    st.subheader('DAY 2')
    dayTwoFirstClass = allClasses.index(st.selectbox(label='Day 2, First Class', options=allClasses))
    if allClasses[dayTwoFirstClass] == 'Other':
      dayTwoFirstClass = st.text_input(label='21Enter Class Name')
      dayTwoFirstClassNumber = st.text_input(label='21Enter Room Number: ')
    elif roomNumbers[dayTwoFirstClass] == '':
      dayTwoFirstClassNumber = st.text_input(label='21Enter Room Number: ')
    elif roomNumbers[dayTwoFirstClass] == 'cityside':
        dayTwoFirstClassNumber = st.selectbox(label='21Choose', options=['in school', 'outside school'])
    else:
        dayTwoFirstClassNumber = roomNumbers[dayTwoFirstClass]

    dayTwoSecondClass = allClasses.index(st.selectbox(label='Day 2, Second Class', options=allClasses))
    if allClasses[dayTwoSecondClass] == 'Other':
      dayTwoSecondClass = st.text_input(label='22Enter Class Name')
      dayTwoSecondClassNumber = st.text_input(label='22Enter Room Number: ')
    elif roomNumbers[dayTwoSecondClass] == '':
      dayTwoSecondClassNumber = st.text_input(label='22Enter Room Number: ')
    elif roomNumbers[dayTwoSecondClass] == 'cityside':
        dayTwoSecondClassNumber = st.selectbox(label='22Choose', options=['in school', 'outside school'])
    else:
        dayTwoSecondClassNumber = roomNumbers[dayTwoSecondClass]

    dayTwoThirdClass = allClasses.index(st.selectbox(label='Day 2, Third Class', options=allClasses))
    if allClasses[dayTwoThirdClass] == 'Other':
      dayTwoThirdClass = st.text_input(label='23Enter Class Name')
      dayTwoThirdClassNumber = st.text_input(label='23Enter Room Number: ')
    elif roomNumbers[dayTwoThirdClass] == '':
      dayTwoThirdClassNumber = st.text_input(label='23Enter Room Number: ')
    elif roomNumbers[dayTwoThirdClass] == 'cityside':
      dayTwoThirdClassNumber = st.selectbox(label='23Choose', options=['in school', 'outside school'])
    else:
      dayTwoThirdClassNumber = roomNumbers[dayTwoThirdClass]

    dayTwoFourthClass = allClasses.index(st.selectbox(label='Day 2, Fourth Class', options=allClasses))
    if allClasses[dayTwoFourthClass] == 'Other':
      dayTwoFourthClass = st.text_input(label='24Enter Class Name')
      dayTwoFourthClassNumber = st.text_input(label='24Enter Room Number: ')
    elif roomNumbers[dayTwoFourthClass] == '':
      dayTwoFourthClassNumber = st.text_input(label='24Enter Room Number: ')
    elif roomNumbers[dayTwoFourthClass] == 'cityside':
      dayTwoFourthClassNumber = st.selectbox(label='24Choose', options=['in school', 'outside school'])
    else:
      dayTwoFourthClassNumber = roomNumbers[dayTwoFourthClass]

    dayTwoFifthClass = allClasses.index(st.selectbox(label='Day 2, Fifth Class', options=allClasses))
    if allClasses[dayTwoFifthClass] == 'Other':
      dayTwoFifthClass = st.text_input(label='25Enter Class Name')
      dayTwoFifthClassNumber = st.text_input(label='25Enter Room Number: ')
    elif roomNumbers[dayTwoFifthClass] == '':
      dayTwoFifthClassNumber = st.text_input(label='25Enter Room Number: ')
    elif roomNumbers[dayTwoFifthClass] == 'cityside':
      dayTwoFifthClassNumber = st.selectbox(label='25Choose', options=['in school', 'outside school'])
    else:
      dayTwoFifthClassNumber = roomNumbers[dayTwoFifthClass]

    dayTwoSixthClass = allClasses.index(st.selectbox(label='Day 2, Sixth Class', options=allClasses))
    if allClasses[dayTwoSixthClass] == 'Other':
      dayTwoSixthClass = st.text_input(label='26Enter Class Name')
      dayTwoSixthClassNumber = st.text_input(label='26Enter Room Number: ')
    elif roomNumbers[dayTwoSixthClass] == '':
      dayTwoSixthClassNumber = st.text_input(label='26Enter Room Number: ')
    elif roomNumbers[dayTwoSixthClass] == 'cityside':
      dayTwoSixthClassNumber = st.selectbox(label='26Choose', options=['in school', 'outside school'])
    else:
      dayTwoSixthClassNumber = roomNumbers[dayTwoSixthClass]

    dayTwoElective = st.text_input(label='Enter Elective Period for Day 2')
    st.subheader('DAY 3')
    dayThreeFirstClass = allClasses.index(st.selectbox(label='Day 3, First Class', options=allClasses))
    if allClasses[dayThreeFirstClass] == 'Other':
      dayThreeFirstClass = st.text_input(label='31Enter Class Name')
      dayThreeFirstClassNumber = st.text_input(label='31Enter Room Number: ')
    elif roomNumbers[dayThreeFirstClass] == '':
      dayThreeFirstClassNumber = st.text_input(label='31Enter Room Number: ')
    elif roomNumbers[dayThreeFirstClass] == 'cityside':
      dayThreeFirstClassNumber = st.selectbox(label='31Choose', options=['in school', 'outside school'])
    else:
      dayThreeFirstClassNumber = roomNumbers[dayThreeFirstClass]

    dayThreeSecondClass = allClasses.index(st.selectbox(label='Day 3, Second Class', options=allClasses))
    if allClasses[dayThreeSecondClass] == 'Other':
      dayThreeSecondClass = st.text_input(label='32Enter Class Name')
      dayThreeSecondClassNumber = st.text_input(label='32Enter Room Number: ')
    elif roomNumbers[dayThreeSecondClass] == '':
      dayThreeSecondClassNumber = st.text_input(label='32Enter Room Number: ')
    elif roomNumbers[dayThreeSecondClass] == 'cityside':
      dayThreeSecondClassNumber = st.selectbox(label='32Choose', options=['in school', 'outside school'])
    else:
      dayThreeSecondClassNumber = roomNumbers[dayThreeSecondClass]

    dayThreeThirdClass = allClasses.index(st.selectbox(label='Day 3, Third Class', options=allClasses))
    if allClasses[dayThreeThirdClass] == 'Other':
      dayThreeThirdClass = st.text_input(label='33Enter Class Name')
      dayThreeThirdClassNumber = st.text_input(label='33Enter Room Number: ')
    elif roomNumbers[dayThreeThirdClass] == '':
      dayThreeThirdClassNumber = st.text_input(label='33Enter Room Number: ')
    elif roomNumbers[dayThreeThirdClass] == 'cityside':
      dayThreeThirdClassNumber = st.selectbox(label='33Choose', options=['in school', 'outside school'])
    else:
      dayThreeThirdClassNumber = roomNumbers[dayThreeThirdClass]

    dayThreeFourthClass = allClasses.index(st.selectbox(label='Day 3, Fourth Class', options=allClasses))
    if allClasses[dayThreeFourthClass] == 'Other':
      dayThreeFourthClass = st.text_input(label='34Enter Class Name')
      dayThreeFourthClassNumber = st.text_input(label='34Enter Room Number: ')
    elif roomNumbers[dayThreeFourthClass] == '':
      dayThreeFourthClassNumber = st.text_input(label='34Enter Room Number: ')
    elif roomNumbers[dayThreeFourthClass] == 'cityside':
      dayThreeFourthClassNumber = st.selectbox(label='34Choose', options=['in school', 'outside school'])
    else:
      dayThreeFourthClassNumber = roomNumbers[dayThreeFourthClass]

    dayThreeFifthClass = allClasses.index(st.selectbox(label='Day 3, Fifth Class', options=allClasses))
    if allClasses[dayThreeFifthClass] == 'Other':
      dayThreeFifthClass = st.text_input(label='35Enter Class Name')
      dayThreeFifthClassNumber = st.text_input(label='35Enter Room Number: ')
    elif roomNumbers[dayThreeFifthClass] == '':
      dayThreeFifthClassNumber = st.text_input(label='35Enter Room Number: ')
    elif roomNumbers[dayThreeFifthClass] == 'cityside':
      dayThreeFifthClassNumber = st.selectbox(label='35Choose', options=['in school', 'outside school'])
    else:
      dayThreeFifthClassNumber = roomNumbers[dayThreeFifthClass]

    dayThreeSixthClass = allClasses.index(st.selectbox(label='Day 3, Sixth Class', options=allClasses))
    if allClasses[dayThreeSixthClass] == 'Other':
      dayThreeSixthClass = st.text_input(label='36Enter Class Name')
      dayThreeSixthClassNumber = st.text_input(label='36Enter Room Number: ')
    elif roomNumbers[dayThreeSixthClass] == '':
      dayThreeSixthClassNumber = st.text_input(label='36Enter Room Number: ')
    elif roomNumbers[dayThreeSixthClass] == 'cityside':
      dayThreeSixthClassNumber = st.selectbox(label='36Choose', options=['in school', 'outside school'])
    else:
      dayThreeSixthClassNumber = roomNumbers[dayThreeSixthClass]

    dayThreeElective = st.text_input(label='Enter Elective Period for Day 3')
    st.subheader('DAY 4')
    dayFourFirstClass = allClasses.index(st.selectbox(label='Day 4, First Class', options=allClasses))
    if allClasses[dayFourFirstClass] == 'Other':
      dayFourFirstClass = st.text_input(label='41Enter Class Name')
      dayFourFirstClassNumber = st.text_input(label='41Enter Room Number: ')
    elif roomNumbers[dayFourFirstClass] == '':
      dayFourFirstClassNumber = st.text_input(label='41Enter Room Number: ')
    elif roomNumbers[dayFourFirstClass] == 'cityside':
      dayFourFirstClassNumber = st.selectbox(label='41Choose', options=['in school', 'outside school'])
    else:
      dayFourFirstClassNumber = roomNumbers[dayFourFirstClass]

    dayFourSecondClass = allClasses.index(st.selectbox(label='Day 4, Second Class', options=allClasses))
    if allClasses[dayFourSecondClass] == 'Other':
      dayFourSecondClass = st.text_input(label='42Enter Class Name')
      dayFourSecondClassNumber = st.text_input(label='42Enter Room Number: ')
    elif roomNumbers[dayFourSecondClass] == '':
      dayFourSecondClassNumber = st.text_input(label='42Enter Room Number: ')
    elif roomNumbers[dayFourSecondClass] == 'cityside':
      dayFourSecondClassNumber = st.selectbox(label='42Choose', options=['in school', 'outside school'])
    else:
      dayFourSecondClassNumber = roomNumbers[dayFourSecondClass]

    dayFourThirdClass = allClasses.index(st.selectbox(label='Day 4, Third Class', options=allClasses))
    if allClasses[dayFourThirdClass] == 'Other':
      dayFourThirdClass = st.text_input(label='43Enter Class Name')
      dayFourThirdClassNumber = st.text_input(label='43Enter Room Number: ')
    elif roomNumbers[dayFourThirdClass] == '':
      dayFourThirdClassNumber = st.text_input(label='43Enter Room Number: ')
    elif roomNumbers[dayFourThirdClass] == 'cityside':
      dayFourThirdClassNumber = st.selectbox(label='43Choose', options=['in school', 'outside school'])
    else:
      dayFourThirdClassNumber = roomNumbers[dayFourThirdClass]

    dayFourFourthClass = allClasses.index(st.selectbox(label='Day 4, Fourth Class', options=allClasses))
    if allClasses[dayFourFourthClass] == 'Other':
      dayFourFourthClass = st.text_input(label='44Enter Class Name')
      dayFourFourthClassNumber = st.text_input(label='44Enter Room Number: ')
    elif roomNumbers[dayFourFourthClass] == '':
      dayFourFourthClassNumber = st.text_input(label='44Enter Room Number: ')
    elif roomNumbers[dayFourFourthClass] == 'cityside':
      dayFourFourthClassNumber = st.selectbox(label='44Choose', options=['in school', 'outside school'])
    else:
      dayFourFourthClassNumber = roomNumbers[dayFourFourthClass]

    dayFourFifthClass = allClasses.index(st.selectbox(label='Day 4, Fifth Class', options=allClasses))
    if allClasses[dayFourFifthClass] == 'Other':
      dayFourFifthClass = st.text_input(label='45Enter Class Name')
      dayFourFifthClassNumber = st.text_input(label='45Enter Room Number: ')
    elif roomNumbers[dayFourFifthClass] == '':
      dayFourFifthClassNumber = st.text_input(label='45Enter Room Number: ')
    elif roomNumbers[dayFourFifthClass] == 'cityside':
      dayFourFifthClassNumber = st.selectbox(label='45Choose', options=['in school', 'outside school'])
    else:
      dayFourFifthClassNumber = roomNumbers[dayFourFifthClass]

    dayFourSixthClass = allClasses.index(st.selectbox(label='Day 4, Sixth Class', options=allClasses))
    if allClasses[dayFourSixthClass] == 'Other':
      dayFourSixthClass = st.text_input(label='46Enter Class Name')
      dayFourSixthClassNumber = st.text_input(label='46Enter Room Number: ')
    elif roomNumbers[dayFourSixthClass] == '':
      dayFourSixthClassNumber = st.text_input(label='46Enter Room Number: ')
    elif roomNumbers[dayFourSixthClass] == 'cityside':
      dayFourSixthClassNumber = st.selectbox(label='46Choose', options=['in school', 'outside school'])
    else:
      dayFourSixthClassNumber = roomNumbers[dayFourSixthClass]

    dayFourElective = st.text_input(label='Enter Elective Period for Day 4')
    st.subheader('DAY 5')
    dayFiveFirstClass = allClasses.index(st.selectbox(label='Day 5, First Class', options=allClasses))
    if allClasses[dayFiveFirstClass] == 'Other':
      dayFiveFirstClass = st.text_input(label='51Enter Class Name')
      dayFiveFirstClassNumber = st.text_input(label='51Enter Room Number: ')
    elif roomNumbers[dayFiveFirstClass] == '':
      dayFiveFirstClassNumber = st.text_input(label='51Enter Room Number: ')
    elif roomNumbers[dayFiveFirstClass] == 'cityside':
      dayFiveFirstClassNumber = st.selectbox(label='51Choose', options=['in school', 'outside school'])
    else:
      dayFiveFirstClassNumber = roomNumbers[dayFiveFirstClass]

    dayFiveSecondClass = allClasses.index(st.selectbox(label='Day 5, Second Class', options=allClasses))
    if allClasses[dayFiveSecondClass] == 'Other':
      dayFiveSecondClass = st.text_input(label='52Enter Class Name')
      dayFiveSecondClassNumber = st.text_input(label='52Enter Room Number: ')
    elif roomNumbers[dayFiveSecondClass] == '':
      dayFiveSecondClassNumber = st.text_input(label='52Enter Room Number: ')
    elif roomNumbers[dayFiveSecondClass] == 'cityside':
      dayFiveSecondClassNumber = st.selectbox(label='52Choose', options=['in school', 'outside school'])
    else:
      dayFiveSecondClassNumber = roomNumbers[dayFiveSecondClass]

    dayFiveThirdClass = allClasses.index(st.selectbox(label='Day 5, Third Class', options=allClasses))
    if allClasses[dayFiveThirdClass] == 'Other':
      dayFiveThirdClass = st.text_input(label='53Enter Class Name')
      dayFiveThirdClassNumber = st.text_input(label='53Enter Room Number: ')
    elif roomNumbers[dayFiveThirdClass] == '':
      dayFiveThirdClassNumber = st.text_input(label='53Enter Room Number: ')
    elif roomNumbers[dayFiveThirdClass] == 'cityside':
      dayFiveThirdClassNumber = st.selectbox(label='53Choose', options=['in school', 'outside school'])
    else:
      dayFiveThirdClassNumber = roomNumbers[dayFiveThirdClass]

    dayFiveFourthClass = allClasses.index(st.selectbox(label='Day 5, Fourth Class', options=allClasses))
    if allClasses[dayFiveFourthClass] == 'Other':
      dayFiveFourthClass = st.text_input(label='54Enter Class Name')
      dayFiveFourthClassNumber = st.text_input(label='54Enter Room Number: ')
    elif roomNumbers[dayFiveFourthClass] == '':
      dayFiveFourthClassNumber = st.text_input(label='54Enter Room Number: ')
    elif roomNumbers[dayFiveFourthClass] == 'cityside':
      dayFiveFourthClassNumber = st.selectbox(label='54Choose', options=['in school', 'outside school'])
    else:
      dayFiveFourthClassNumber = roomNumbers[dayFiveFourthClass]

    dayFiveFifthClass = allClasses.index(st.selectbox(label='Day 5, Fifth Class', options=allClasses))
    if allClasses[dayFiveFifthClass] == 'Other':
      dayFiveFifthClass = st.text_input(label='55Enter Class Name')
      dayFiveFifthClassNumber = st.text_input(label='55Enter Room Number: ')
    elif roomNumbers[dayFiveFifthClass] == '':
      dayFiveFifthClassNumber = st.text_input(label='55Enter Room Number: ')
    elif roomNumbers[dayFiveFifthClass] == 'cityside':
      dayFiveFifthClassNumber = st.selectbox(label='55Choose', options=['in school', 'outside school'])
    else:
      dayFiveFifthClassNumber = roomNumbers[dayFiveFifthClass]

    dayFiveSixthClass = allClasses.index(st.selectbox(label='Day 5, Sixth Class', options=allClasses))
    if allClasses[dayFiveSixthClass] == 'Other':
      dayFiveSixthClass = st.text_input(label='56Enter Class Name')
      dayFiveSixthClassNumber = st.text_input(label='56Enter Room Number: ')
    elif roomNumbers[dayFiveSixthClass] == '':
      dayFiveSixthClassNumber = st.text_input(label='56Enter Room Number: ')
    elif roomNumbers[dayFiveSixthClass] == 'cityside':
      dayFiveSixthClassNumber = st.selectbox(label='56Choose', options=['in school', 'outside school'])
    else:
      dayFiveSixthClassNumber = roomNumbers[dayFiveSixthClass]

    dayFiveElective = st.text_input(label='Enter Elective Period for Day 5')
    st.subheader('DAY 6')
    daySixFirstClass = allClasses.index(st.selectbox(label='Day 6, First Class', options=allClasses))
    if allClasses[daySixFirstClass] == 'Other':
      daySixFirstClass = st.text_input(label='61Enter Class Name')
      daySixFirstClassNumber = st.text_input(label='61Enter Room Number: ')
    elif roomNumbers[daySixFirstClass] == '':
      daySixFirstClassNumber = st.text_input(label='61Enter Room Number: ')
    elif roomNumbers[daySixFirstClass] == 'cityside':
      daySixFirstClassNumber = st.selectbox(label='61Choose', options=['in school', 'outside school'])
    else:
      daySixFirstClassNumber = roomNumbers[daySixFirstClass]

    daySixSecondClass = allClasses.index(st.selectbox(label='Day 6, Second Class', options=allClasses))
    if allClasses[daySixSecondClass] == 'Other':
      daySixSecondClass = st.text_input(label='62Enter Class Name')
      daySixSecondClassNumber = st.text_input(label='62Enter Room Number: ')
    elif roomNumbers[daySixSecondClass] == '':
      daySixSecondClassNumber = st.text_input(label='62Enter Room Number: ')
    elif roomNumbers[daySixSecondClass] == 'cityside':
      daySixSecondClassNumber = st.selectbox(label='62Choose', options=['in school', 'outside school'])
    else:
      daySixSecondClassNumber = roomNumbers[daySixSecondClass]

    daySixThirdClass = allClasses.index(st.selectbox(label='Day 6, Third Class', options=allClasses))
    if allClasses[daySixThirdClass] == 'Other':
      daySixThirdClass = st.text_input(label='63Enter Class Name')
      daySixThirdClassNumber = st.text_input(label='63Enter Room Number: ')
    elif roomNumbers[daySixThirdClass] == '':
      daySixThirdClassNumber = st.text_input(label='63Enter Room Number: ')
    elif roomNumbers[daySixThirdClass] == 'cityside':
      daySixThirdClassNumber = st.selectbox(label='63Choose', options=['in school', 'outside school'])
    else:
      daySixThirdClassNumber = roomNumbers[daySixThirdClass]

    daySixFourthClass = allClasses.index(st.selectbox(label='Day 6, Fourth Class', options=allClasses))
    if allClasses[daySixFourthClass] == 'Other':
      daySixFourthClass = st.text_input(label='64Enter Class Name')
      daySixFourthClassNumber = st.text_input(label='64Enter Room Number: ')
    elif roomNumbers[daySixFourthClass] == '':
      daySixFourthClassNumber = st.text_input(label='64Enter Room Number: ')
    elif roomNumbers[daySixFourthClass] == 'cityside':
      daySixFourthClassNumber = st.selectbox(label='64Choose', options=['in school', 'outside school'])
    else:
      daySixFourthClassNumber = roomNumbers[daySixFourthClass]

    daySixFifthClass = allClasses.index(st.selectbox(label='Day 6, Fifth Class', options=allClasses))
    if allClasses[daySixFifthClass] == 'Other':
      daySixFifthClass = st.text_input(label='65Enter Class Name')
      daySixFifthClassNumber = st.text_input(label='65Enter Room Number: ')
    elif roomNumbers[daySixFifthClass] == '':
      daySixFifthClassNumber = st.text_input(label='65Enter Room Number: ')
    elif roomNumbers[daySixFifthClass] == 'cityside':
      daySixFifthClassNumber = st.selectbox(label='65Choose', options=['in school', 'outside school'])
    else:
      daySixFifthClassNumber = roomNumbers[daySixFifthClass]

    daySixSixthClass = allClasses.index(st.selectbox(label='Day 6, Sixth Class', options=allClasses))
    if allClasses[daySixSixthClass] == 'Other':
      daySixSixthClass = st.text_input(label='66Enter Class Name')
      daySixSixthClassNumber = st.text_input(label='66Enter Room Number: ')
    elif roomNumbers[daySixSixthClass] == '':
      daySixSixthClassNumber = st.text_input(label='66Enter Room Number: ')
    elif roomNumbers[daySixSixthClass] == 'cityside':
        daySixSixthClassNumber = st.selectbox(label='66Choose', options=['in school', 'outside school'])
    else:
        daySixSixthClassNumber = roomNumbers[daySixSixthClass]

    daySixElective = st.text_input(label='Enter Elective Period for Day 6')
    st.subheader('DAY 7')
    daySevenFirstClass = allClasses.index(st.selectbox(label='Day 7, First Class', options=allClasses))
    if allClasses[daySevenFirstClass] == 'Other':
      daySevenFirstClass = st.text_input(label='71Enter Class Name')
      daySevenFirstClassNumber = st.text_input(label='71Enter Room Number: ')
    elif roomNumbers[daySevenFirstClass] == '':
      daySevenFirstClassNumber = st.text_input(label='71Enter Room Number: ')
    elif roomNumbers[daySevenFirstClass] == 'cityside':
      daySevenFirstClassNumber = st.selectbox(label='71Choose', options=['in school', 'outside school'])
    else:
      daySevenFirstClassNumber = roomNumbers[daySevenFirstClass]

    daySevenSecondClass = allClasses.index(st.selectbox(label='Day 7, Second Class', options=allClasses))
    if allClasses[daySevenSecondClass] == 'Other':
      daySevenSecondClass = st.text_input(label='72Enter Class Name')
      daySevenSecondClassNumber = st.text_input(label='72Enter Room Number: ')
    elif roomNumbers[daySevenSecondClass] == '':
      daySevenSecondClassNumber = st.text_input(label='72Enter Room Number: ')
    elif roomNumbers[daySevenSecondClass] == 'cityside':
      daySevenSecondClassNumber = st.selectbox(label='72Choose', options=['in school', 'outside school'])
    else:
      daySevenSecondClassNumber = roomNumbers[daySevenSecondClass]

    daySevenThirdClass = allClasses.index(st.selectbox(label='Day 7, Third Class', options=allClasses))
    if allClasses[daySevenThirdClass] == 'Other':
      daySevenThirdClass = st.text_input(label='73Enter Class Name')
      daySevenThirdClassNumber = st.text_input(label='73Enter Room Number: ')
    elif roomNumbers[daySevenThirdClass] == '':
      daySevenThirdClassNumber = st.text_input(label='73Enter Room Number: ')
    elif roomNumbers[daySevenThirdClass] == 'cityside':
      daySevenThirdClassNumber = st.selectbox(label='73Choose', options=['in school', 'outside school'])
    else:
      daySevenThirdClassNumber = roomNumbers[daySevenThirdClass]

    daySevenFourthClass = allClasses.index(st.selectbox(label='Day 7, Fourth Class', options=allClasses))
    if allClasses[daySevenFourthClass] == 'Other':
      daySevenFourthClass = st.text_input(label='74Enter Class Name')
      daySevenFourthClassNumber = st.text_input(label='74Enter Room Number: ')
    elif roomNumbers[daySevenFourthClass] == '':
      daySevenFourthClassNumber = st.text_input(label='74Enter Room Number: ')
    elif roomNumbers[daySevenFourthClass] == 'cityside':
      daySevenFourthClassNumber = st.selectbox(label='74Choose', options=['in school', 'outside school'])
    else:
      daySevenFourthClassNumber = roomNumbers[daySevenFourthClass]

    daySevenFifthClass = allClasses.index(st.selectbox(label='Day 7, Fifth Class', options=allClasses))
    if allClasses[daySevenFifthClass] == 'Other':
      daySevenFifthClass = st.text_input(label='75Enter Class Name')
      daySevenFifthClassNumber = st.text_input(label='75Enter Room Number: ')
    elif roomNumbers[daySevenFifthClass] == '':
      daySevenFifthClassNumber = st.text_input(label='75Enter Room Number: ')
    elif roomNumbers[daySevenFifthClass] == 'cityside':
      daySevenFifthClassNumber = st.selectbox(label='75Choose', options=['in school', 'outside school'])
    else:
      daySevenFifthClassNumber = roomNumbers[daySevenFifthClass]

    daySevenSixthClass = allClasses.index(st.selectbox(label='Day 7, Sixth Class', options=allClasses))
    if allClasses[daySevenSixthClass] == 'Other':
      daySevenSixthClass = st.text_input(label='76Enter Class Name')
      daySevenSixthClassNumber = st.text_input(label='76Enter Room Number: ')
    elif roomNumbers[daySevenSixthClass] == '':
      daySevenSixthClassNumber = st.text_input(label='76Enter Room Number: ')
    elif roomNumbers[daySevenSixthClass] == 'cityside':
      daySevenSixthClassNumber = st.selectbox(label='76Choose', options=['in school', 'outside school'])
    else:
      daySevenSixthClassNumber = roomNumbers[daySevenSixthClass]

    daySevenElective = st.text_input(label='Enter Elective Period for Day 7')
    st.subheader('DAY 8')
    dayEightFirstClass = allClasses.index(st.selectbox(label='Day 8, First Class', options=allClasses))
    if allClasses[dayEightFirstClass] == 'Other':
      dayEightFirstClass = st.text_input(label='81Enter Class Name')
      dayEightFirstClassNumber = st.text_input(label='81Enter Room Number: ')
    elif roomNumbers[dayEightFirstClass] == '':
      dayEightFirstClassNumber = st.text_input(label='81Enter Room Number: ')
    elif roomNumbers[dayEightFirstClass] == 'cityside':
      dayEightFirstClassNumber = st.selectbox(label='81Choose', options=['in school', 'outside school'])
    else:
      dayEightFirstClassNumber = roomNumbers[dayEightFirstClass]

    dayEightSecondClass = allClasses.index(st.selectbox(label='Day 8, Second Class', options=allClasses))
    if allClasses[dayEightSecondClass] == 'Other':
      dayEightSecondClass = st.text_input(label='82Enter Class Name')
      dayEightSecondClassNumber = st.text_input(label='82Enter Room Number: ')
    elif roomNumbers[dayEightSecondClass] == '':
      dayEightSecondClassNumber = st.text_input(label='82Enter Room Number: ')
    elif roomNumbers[dayEightSecondClass] == 'cityside':
      dayEightSecondClassNumber = st.selectbox(label='82Choose', options=['in school', 'outside school'])
    else:
      dayEightSecondClassNumber = roomNumbers[dayEightSecondClass]

    dayEightThirdClass = allClasses.index(st.selectbox(label='Day 8, Third Class', options=allClasses))
    if allClasses[dayEightThirdClass] == 'Other':
      dayEightThirdClass = st.text_input(label='83Enter Class Name')
      dayEightThirdClassNumber = st.text_input(label='83Enter Room Number: ')
    elif roomNumbers[dayEightThirdClass] == '':
      dayEightThirdClassNumber = st.text_input(label='83Enter Room Number: ')
    elif roomNumbers[dayEightThirdClass] == 'cityside':
      dayEightThirdClassNumber = st.selectbox(label='83Choose', options=['in school', 'outside school'])
    else:
      dayEightThirdClassNumber = roomNumbers[dayEightThirdClass]

    dayEightFourthClass = allClasses.index(st.selectbox(label='Day 8, Fourth Class', options=allClasses))
    if allClasses[dayEightFourthClass] == 'Other':
      dayEightFourthClass = st.text_input(label='84Enter Class Name')
      dayEightFourthClassNumber = st.text_input(label='84Enter Room Number: ')
    elif roomNumbers[dayEightFourthClass] == '':
      dayEightFourthClassNumber = st.text_input(label='84Enter Room Number: ')
    elif roomNumbers[dayEightFourthClass] == 'cityside':
      dayEightFourthClassNumber = st.selectbox(label='84Choose', options=['in school', 'outside school'])
    else:
      dayEightFourthClassNumber = roomNumbers[dayEightFourthClass]

    dayEightFifthClass = allClasses.index(st.selectbox(label='Day 8, Fifth Class', options=allClasses))
    if allClasses[dayEightFifthClass] == 'Other':
      dayEightFifthClass = st.text_input(label='85Enter Class Name')
      dayEightFifthClassNumber = st.text_input(label='85Enter Room Number: ')
    elif roomNumbers[dayEightFifthClass] == '':
      dayEightFifthClassNumber = st.text_input(label='85Enter Room Number: ')
    elif roomNumbers[dayEightFifthClass] == 'cityside':
      dayEightFifthClassNumber = st.selectbox(label='85Choose', options=['in school', 'outside school'])
    else:
      dayEightFifthClassNumber = roomNumbers[dayEightFifthClass]

    dayEightSixthClass = allClasses.index(st.selectbox(label='Day 8, Sixth Class', options=allClasses))
    if allClasses[dayEightSixthClass] == 'Other':
        dayEightSixthClass = st.text_input(label='86Enter Class Name')
        dayEightSixthClassNumber = st.text_input(label='86Enter Room Number: ')
    elif roomNumbers[dayEightSixthClass] == '':
      dayEightSixthClassNumber = st.text_input(label='86Enter Room Number: ')
    elif roomNumbers[dayEightSixthClass] == 'cityside':
      dayEightSixthClassNumber = st.selectbox(label='86Choose', options=['in school', 'outside school'])
    else:
      dayEightSixthClassNumber = roomNumbers[dayEightSixthClass]

    dayEightElective = st.text_input(label='Enter Elective Period for Day 8')
    st.write('---')
    create = st.button(label='Create')
    if create:
      class_days = [
        [dayOneFirstClass, dayOneSecondClass, dayOneThirdClass, dayOneFourthClass, dayOneFifthClass, dayOneSixthClass, dayOneElective],
        [dayTwoFirstClass, dayTwoSecondClass, dayTwoThirdClass, dayTwoFourthClass, dayTwoFifthClass, dayTwoSixthClass, dayTwoElective],
        [dayThreeFirstClass, dayThreeSecondClass, dayThreeThirdClass, dayThreeFourthClass, dayThreeFifthClass, dayThreeSixthClass, dayThreeElective],
        [dayFourFirstClass, dayFourSecondClass, dayFourThirdClass, dayFourFourthClass, dayFourFifthClass, dayFourSixthClass, dayFourElective],
        [dayFiveFirstClass, dayFiveSecondClass, dayFiveThirdClass, dayFiveFourthClass, dayFiveFifthClass, dayFiveSixthClass, dayFiveElective],
        [daySixFirstClass, daySixSecondClass, daySixThirdClass, daySixFourthClass, daySixFifthClass, daySixSixthClass, daySixElective],
        [daySevenFirstClass, daySevenSecondClass, daySevenThirdClass, daySevenFourthClass, daySevenFifthClass, daySevenSixthClass, daySevenElective],
        [dayEightFirstClass, dayEightSecondClass, dayEightThirdClass, dayEightFourthClass, dayEightFifthClass, dayEightSixthClass, dayEightElective]
      ]

      class_room_number = [
        [dayOneFirstClassNumber, dayOneSecondClassNumber, dayOneThirdClassNumber, dayOneFourthClassNumber, dayOneFifthClassNumber, dayOneSixthClassNumber],
        [dayTwoFirstClassNumber, dayTwoSecondClassNumber, dayTwoThirdClassNumber, dayTwoFourthClassNumber, dayTwoFifthClassNumber, dayTwoSixthClassNumber],
        [dayThreeFirstClassNumber, dayThreeSecondClassNumber, dayThreeThirdClassNumber, dayThreeFourthClassNumber, dayThreeFifthClassNumber, dayThreeSixthClassNumber],
        [dayFourFirstClassNumber, dayFourSecondClassNumber, dayFourThirdClassNumber, dayFourFourthClassNumber, dayFourFifthClassNumber, dayFourSixthClassNumber],
        [dayFiveFirstClassNumber, dayFiveSecondClassNumber, dayFiveThirdClassNumber, dayFiveFourthClassNumber, dayFiveFifthClassNumber, dayFiveSixthClassNumber],
        [daySixFirstClassNumber, daySixSecondClassNumber, daySixThirdClassNumber, daySixFourthClassNumber, daySixFifthClassNumber, daySixSixthClassNumber],
        [daySevenFirstClassNumber, daySevenSecondClassNumber, daySevenThirdClassNumber, daySevenFourthClassNumber, daySevenFifthClassNumber, daySevenSixthClassNumber],
        [dayEightFirstClassNumber, dayEightSecondClassNumber, dayEightThirdClassNumber, dayEightFourthClassNumber, dayEightFifthClassNumber, dayEightSixthClassNumber]
      ]
      for i in range(len(class_days)):
        for j in range(len(class_days[i])):
          if j == 6:
            roomNum = None
          else:
            roomNum = class_room_number[i][j]
          if isinstance(class_days[i][j], int) and 0 <= class_days[i][j] < len(allClasses):
            class_days[i][j] = {'className': allClasses[class_days[i][j]], 'classNumber': roomNum}
          else:
            class_days[i][j] = {'className': class_days[i][j], 'classNumber': roomNum}

      schedule = {'_id': userAccount['_id'], '1': class_days[0], '2': class_days[1], '3': class_days[2], '4': class_days[3], '5': class_days[4], '6': class_days[5], '7': class_days[6], '8': class_days[7], 'dateCreated': datetime.utcnow().isoformat()}
      Schedules.insert_one(schedule)
      st.rerun()
