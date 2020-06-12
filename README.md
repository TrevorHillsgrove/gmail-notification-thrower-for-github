# gmail-notification-thrower-for-github
 A simple script to help see Github notifications easier, without having to sync a Gmail account to an email client


***Purpose:*** Make parsing Github notifications sent to a Gmail inbox a little easier,
without having to throw notifications for all Gmail emails

FOR MAC OS ONLY!!!

***DEPENDENCIES:***
Follow this tutorial for obtaining your credentials.json file (renamed googleCredentials.json in this script)
https://developers.google.com/gmail/api/quickstart/python

Make sure you have terminal-notifier installed on your system (https://github.com/julienXX/terminal-notifier), can be installed with homebrew
install dependency pync with pip: https://pypi.org/project/pync/

Make sure that all Github emails you are receiving auto-add a custom tag you've named GithubNotifications

If you want, you can also install this in your crontab with crontab -e
My crontab (only runs on workdays from 8 am to 5:59 pm, at 5 minute intervals)
`0,5,10,15,20,25,30,35,40,45,50,55 8-17 * * 1-5  cd scriptPath && /usr/bin/python scriptPath/emailNotification.py`

Note: If you are having issues with cron accessing Python, you may need to give cron full-disk access: https://blog.bejarano.io/fixing-cron-jobs-in-mojave/
