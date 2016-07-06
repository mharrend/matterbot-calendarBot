 # -*- coding: utf-8 -*-
from exchangelib import DELEGATE
from exchangelib.account import Account
from exchangelib.configuration import Configuration
from exchangelib.ewsdatetime import EWSDateTime, EWSTimeZone
from exchangelib.folders import CalendarItem
from exchangelib.services import IdOnly

from .calendarBotSettings import *

import sqlite3
import datetime
import re
import html2text

def initEventStorage():
    # Open sqlite database, up to now it is used to store calendarNames / Outlook categories and Mattermost groups in which calendar events should be posted.
    # The calendar events are stored in an Outlook calendar and also in the sqlite database up to now.
    try: 
        conn = sqlite3.connect(calendarSettings['DatabaseName'])
        cursor=conn.cursor()
    except Exception as e:
        print ("Could not open sqlite database due to following exception:\n {0} \n {1}".format(e.__doc__, e.message))

    # Open outlook calendar
    try:
        config = Configuration(username=outlookSettings['Username'], password=outlookSettings['Password'])
        account = Account(primary_smtp_address=outlookSettings['Email'], config=config, autodiscover=True, access_type=DELEGATE)
    except Exception as e:
        print ("Could not open Outlook calendar due to following exception:\n {0} \n {1}".format(e.__doc__, e.message))

    # Set timezone needed later, note: only Copenhagen is mapped but it is the same timezone as Berlin
    tz = EWSTimeZone.timezone('Europe/Copenhagen')

    # Create table which contains subcalendars
    # calendarName: Name which is refered to add an event, calendarMattermostGroup: group in which events should be published
    # calendarName is rewritten in an Outlook calendar category to be stored in Outlook calendar
    try:
        createCalendarTable = "CREATE TABLE IF NOT EXISTS 'calendarTable' (id INTEGER PRIMARY KEY AUTOINCREMENT, calendarName TEXT, calendarMattermostGroup TEXT)"
        conn.execute(createCalendarTable)
    except Exception as e:
        print ("Could not access / create sqlite calendar due to following exception:\n {0} \n {1}".format(e.__doc__, e.message))

    return conn, cursor, tz, account
        
        
def checkIfCalendarExists(calendarName):
    """ Check if calendar already exists using sqlite_master table"""
    conn, cursor, tz, account = initEventStorage()
    # calendarName in lowercase to handle problems with finding it in database
    calendarName = calendarName.lower()
    testCalendarExists = "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'  AND name = '{0}'".format(calendarName)
    data = cursor.execute(testCalendarExists).fetchone()
    if data[0] != 0:
        return True
    else:
        return False
        
def createNewCalendar(calendarName, calendarGroup):
    """ Create a new calendar if it exists not already and add it to calendarTable"""
    conn, cursor, tz, account = initEventStorage()
    # calendarName in lowercase to handle problems with finding it in in database
    calendarName = calendarName.lower()
    calendarGroup = calendarGroup.lower()
    if checkIfCalendarExists(calendarName):
        return False, "Calendar {0} exists already".format(calendarName)
    else:
        createCalendar = "CREATE TABLE IF NOT EXISTS '{0}' (id INTEGER PRIMARY KEY AUTOINCREMENT, eventName TEXT, eventDescription TEXT, eventStartDate TEXT, eventEndDate TEXT, eventDuration TEXT)".format(calendarName)
        conn.execute(createCalendar)
        addCalendarToCalendarTable = "INSERT INTO 'calendarTable' (calendarName, calendarMattermostGroup) VALUES ('{0}', '{1}')".format(calendarName, calendarGroup)
        conn.execute(addCalendarToCalendarTable)
        conn.commit()
        return True, "Calendar {0} created".format(calendarName)
      
def addEvent (calendarName, eventName, eventDescription, eventStartDate, eventEndDate):
    """ Add a new event to a calendar
    
    eventDescription can be empty
    eventDuration is calculated later by using eventStartDate and eventEndDate
    calendarName is stored as an Outlook calendar category
    """
    conn, cursor, tz, account = initEventStorage()
    # calendarName in lowercase to handle problems with finding it in database
    calendarName = calendarName.lower()
    if not checkIfCalendarExists(calendarName):
        return False, "Calendar {0} does not exist".format(calendarName)
    
    if not eventName:
        return False, "Event name is empty"
    
    try:
        convEventStartDate = datetime.datetime.strptime(eventStartDate, "%d.%m.%Y %H:%M")
    except ValueError:
        return False, "Event start date {0} could not be converted to date, Date format should be: %d.%m.%Y %H:%M".format(eventStartDate)
    
    try:
        convEventEndDate = datetime.datetime.strptime(eventEndDate, "%d.%m.%Y %H:%M")
    except ValueError:
        return False, "Event end date {0} could not be converted to date, Date format should be: %d.%m.%Y %H:%M".format(eventEndDate)    
    
    timeDuration = convEventEndDate - convEventStartDate
    if timeDuration < datetime.timedelta(0):
        return False, "Event duration is negative, please check start date {0} and end date {1}".format(convEventStartDate, convEventEndDate)
    eventDuration = str(timeDuration)
    
    # Add event to sqlite calendar
    addEventToSQLCalendar = "INSERT INTO '{0}' (eventName, eventDescription, eventStartDate, eventEndDate, eventDuration) VALUES ('{1}', '{2}', '{3}', '{4}', '{5}')".format(calendarName, eventName, eventDescription, convEventStartDate, convEventEndDate, eventDuration)
    conn.execute(addEventToSQLCalendar)
    conn.commit()    
    
    # Create and add event to outlook calendar
    # A list of calendar items is required, so let us create one.
    calendar_items = []
    calendar_items.append(CalendarItem(
        start=tz.localize(EWSDateTime(convEventStartDate.year, convEventStartDate.month, convEventStartDate.day, convEventStartDate.hour, convEventStartDate.minute, convEventStartDate.second, convEventStartDate.microsecond)),
        end=tz.localize(EWSDateTime(convEventEndDate.year, convEventEndDate.month, convEventEndDate.day, convEventEndDate.hour, convEventEndDate.minute, convEventEndDate.second, convEventEndDate.microsecond)),
        subject=eventName,
        body=eventDescription,
        location='empty',
        categories=[calendarName],
    ))
    res = account.calendar.add_items(calendar_items)
    
    return True, "Event {0} created".format(eventName)



def showAgenda (calendarName = '', eventStartDate = '', eventEndDate = '', deleteAfterwards = False):
    """ 
    Shows Agenda using the calendar in Outlook

    If no calendarName is given which is used as a category all events are shown
    if calendarName is given only events of this category are shown
    if start and end date are given the agenda of this time span is shown, otherwise agenda of today is shown.
    """
    conn, cursor, tz, account = initEventStorage()
    # calendarName in lowercase to handle problems with finding it in database
    calendarName = calendarName.lower()
    # Strip whitespace
    calendarName = calendarName.strip()
    # Check if calendar exists otherwise, we cannot show its agenda
    if  calendarName == '':
        calendarCategory = None
    elif checkIfCalendarExists(calendarName):
        calendarCategory = [calendarName]
    else:
        return False, "Calendar {0} does not exist, agenda cannot be shown. Try command without stating a calendar".format(calendarName)

    # If start and end date is given check if it is a positive time span
    if eventStartDate  or eventEndDate:
        try:
            convEventStartDate = datetime.datetime.strptime(eventStartDate, "%d.%m.%Y %H:%M")
        except ValueError:
            try:
                convEventStartDate = datetime.datetime.strptime(eventStartDate, "%d.%m.%Y")
                convEventStartDate = convEventStartDate.replace(hour=0, minute = 00)
            except ValueError:
                return False, "Event start date {0} could not be converted to date, Date format should be either: %d.%m.%Y or: %d.%m.%Y %H:%M".format(eventStartDate)

        try:
            convEventEndDate = datetime.datetime.strptime(eventEndDate, "%d.%m.%Y %H:%M")
        except ValueError:
            try:
                convEventEndDate = datetime.datetime.strptime(eventEndDate, "%d.%m.%Y")
                convEventEndDate = convEventEndDate.replace(hour= 23, minute = 59)
            except ValueError:
                return False, "Event end date {0} could not be converted to date, Date format should be either: %d.%m.%Y or: %d.%m.%Y %H:%M".format(eventEndDate)    
    
        timeDuration = convEventEndDate - convEventStartDate
        if timeDuration < datetime.timedelta(0):
            return False, "Event duration is negative, please check start date {0} and end date {1}".format(convEventStartDate, convEventEndDate)
        eventDuration = str(timeDuration)
    # use today for the agenda
    else:
        nowDate = datetime.datetime.now()
        convEventStartDate =  nowDate.replace(hour=0, minute = 00)
        convEventEndDate = nowDate.replace(hour = 23, minute = 59)


    # Get Exchange ID and of the calendar items 
    try: 
        startDate=tz.localize(EWSDateTime(convEventStartDate.year, convEventStartDate.month, convEventStartDate.day, convEventStartDate.hour, convEventStartDate.minute))
        endDate=tz.localize(EWSDateTime(convEventEndDate.year, convEventEndDate.month, convEventEndDate.day, convEventEndDate.hour, convEventEndDate.minute))
        ids = account.calendar.find_items(start=startDate, end=endDate, categories=calendarCategory, shape=IdOnly,)

	# Get full selected items
        items = account.calendar.get_items(ids)

        # Delete selected items after they have been shown in calendarBot
        if deleteAfterwards:
            res = account.calendar.delete_items(ids)

    except Exception as e:
        return False, "Could not access event items in Outlook calendar due to following exception:\n {0} \n {1}".format(e.__doc__, e.message)

    return True, items

