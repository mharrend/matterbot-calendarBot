# matterbot-calendarBot
Calendar Bot for mattermost

## Requirements
This bot is making use of
* Mattermost http://www.mattermost.org
* Exchangelib https://github.com/ecederstrand/exchangelib/tree/master/exchangelib
* Matterhook https://github.com/numberly/matterhook
* Mattermost_bot https://github.com/LPgenerator/mattermost_bot

## Purpose
* The calendarBot can be used to display events from an Microsoft Exchange 2007-2016 Server or Office365 account in Mattermost.
  * By using the category field of an event it is possible to which Mattermost group an event is posted.
  * If the Mattermost group cannot be found, a default channel is used.
  * A global setting exists to define in which time in advance an event is posted in Mattermost.
  * By default events are deleted for now after they have been posted to Mattermost. In the future, most likely an option will allow to just mask these events.
* Furthermore, a plugin for the Mattermost_bot bot exists, which allows to create events in Mattermost itself. Have a look at https://github.com/mharrend/matterbot-plugins-server/blob/master/calendar.py
  * Using this plugin events and subcalendars can be created.
  * The events and calendars are stored in the online account and also saved in a local SQLite database.
  * The plugin also allows to show the agenda of today using all subcalendars or specifying only one subcalendar.

## Setup
The configuration is done in the calendarBotSettings.py file:
* mattermostSettings
  * URL: Url to your Mattermost installation
  * ApiKey: Key for incoming webhook, must created in Mattermost using the integrations settings. More information can be found in the Matterhook documentation
  * Username: Name of the calendarBot that is used in Mattermost
  * IconURL: Definition of an icon shown in Mattermost, e.g. https://commons.wikimedia.org/wiki/File:Gnome-x-office-calendar.svg
  * DefaultChannel: Channel in which events are posted if the group defined in the event cannot be found
* outlookSettings
  * Email: Emailadress of account which is used to look up server, more documentation can be found in Exchangelib 
  * Username: Username required to log into email account
  * Password: Password required to log into email account
* calendarSettings
  * DatabaseName: Name of local SQLite database
  * CheckInterval: Amount of seconds between checks for upcoming events
  * TimespanToCheck: Definition of minute interval which is used for checking of upcoming events
