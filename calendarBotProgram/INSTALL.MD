# Installation of calendarBot monitoring script

## Prerequisites

1. Install the calendarBot module via pip3 calendarBot
2. Set the proper settings in /usr/local/lib/python3[XXX]/dist-packages/calendarBot/calendarBotSettings.py

## Installation of calendarBot monitoring script

1. Git checkout out repository
2. Copy calendarBotProgram directory to /opt/calendarBot-installation/calendarBotProgram
3. Make sure that the calendarBot monitoring script works by starting it manually via /opt/calendarBot-installation/calendarBotProgram/calendarBot. Please note that the python script should run forever if you do not interrupt it.
4. The following steps make sure that the calendarBot monitoring script starts automatically.
5. Copy calendarBot-init.d file to /etc/init.d/calendarBot
6. Test if the init script works by typing
  * /etc/init.d/calendarBot start
  * /etc/init.d/calendarBot status
