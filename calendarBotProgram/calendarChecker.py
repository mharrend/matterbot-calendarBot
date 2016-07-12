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
            eventContent = '### **{0}**\nTime: {1} - {2} (KIT time)\nDetails: {3}Location: {4}\n\n'.format(item.subject,item.start.astimezone(EWSTimeZone.timezone('Europe/Copenhagen')).strftime('%H:%M'),item.end.astimezone(EWSTimeZone.timezone('Europe/Copenhagen')).strftime('%H:%M'), html2text.html2text(item.body), item.location)
            for subcalendar in item.categories:
                try:
                    mattermostHook.send(eventContent, channel=subcalendar)
                except Exception as e:
                    messageContent = eventContent + '\n Error occured: \n {0} \n'.format(e.__doc__)
                    mattermostHook.send(messageContent, channel=mattermostSettings['DefaultChannel'])

timer = RepeatedTimer(calendarSettings['CheckInterval'], checkCalendarForUpcomingEvents)
