#!/usr/bin/python3

# Access to mattermost
from matterhook import Webhook

import datetime
import html2text


from calendarBot.calendarBotSettings import *
from calendarBot.calendarApi import *
from calendarBot.calendarTimer import *

# Initialize Mattermost access
mattermostHook = Webhook(mattermostSettings['URL'], mattermostSettings['ApiKey'])
mattermostHook.username = mattermostSettings['Username']
mattermostHook.icon_url = mattermostSettings['IconURL']

def checkCalendarForUpcomingEvents():
    """
    Checks calendar for upcoming events
    """
    nowDate = datetime.datetime.now()
    laterDate = nowDate + datetime.timedelta(minutes = calendarSettings['TimespanToCheck'])
    successful, res = showAgenda('', nowDate.strftime("%d.%m.%Y %H:%M"), laterDate.strftime("%d.%m.%Y %H:%M"), True)
    if successful:
        for item in res:
            eventContent = 'EventName: {0}\n EventBeschreibung: {1}\n EventStart: {2}\n EventEnd: {3}\n EventLocation: {4}\n EventCategory: {5}\n\n'.format(item.subject, html2text.html2text(item.body),item.start.astimezone(EWSTimeZone.timezone('Europe/Copenhagen')), item.end.astimezone(EWSTimeZone.timezone('Europe/Copenhagen')), item.location, item.categories)
            for subcalendar in item.categories:
                try:
                    mattermostHook.send(eventContent, channel=subcalendar)
                except Exception as e:
                    messageContent = eventContent + '\n Error occured: \n {0} \n'.format(e.__doc__)
                    mattermostHook.send(messageContent, channel=mattermostSettings['DefaultChannel'])

timer = RepeatedTimer(calendarSettings['CheckInterval'], checkCalendarForUpcomingEvents)
