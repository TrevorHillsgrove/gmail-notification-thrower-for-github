from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import pync
import time
from datetime import date
import base64
import re
import sys

# Purpose: Make parsing Github notifications sent to a Gmail inbox a little easier,
# without having to throw notifications for all Gmail emails

# FOR MAC OS ONLY!!!

# DEPENDENCIES:
# Follow this tutorial for obtaining your credentials.json file (renamed googleCredentials.json in this script)
# https://developers.google.com/gmail/api/quickstart/python

# Make sure you have terminal-notifier installed on your system (https://github.com/julienXX/terminal-notifier), can be installed with homebrew
# install dependency pync with pip: https://pypi.org/project/pync/

# Make sure that all Github emails you are receiving auto-add a custom tag you've named GithubNotifications

# If you want, you can also install this in your crontab with crontab -e
# My crontab (only runs on workdays from 8 am to 5:59 pm, at 5 minute intervals)
# 0,5,10,15,20,25,30,35,40,45,50,55 8-17 * * 1-5  cd scriptPath && /usr/bin/python scriptPath/emailNotification.py

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Get all unread GithubNotifications messages
def getMessages(labelId, service):
    emails = []

    try:
        # Gmail's after tag breaks for most emails if you include a .0, so we need to remove that with rstrip
        query = 'after:'+(str(time.mktime(date.today().timetuple()))).rstrip('0').rstrip('.')
        emailResults = service.users().messages().list(userId='me', labelIds=[labelId, 'UNREAD'], q=query).execute()
        
        if 'messages' in emailResults:
            emails.extend(emailResults['messages'])

        while 'nextPageToken' in emailResults:
            page_token = emailResults['nextPageToken']
            response = service.users().messages().list(userId='me', labelIds=[labelId, 'UNREAD'], q=query, pageToken=page_token).execute()
            emails.extend(response['messages'])

        return emails
    except:
        return emails

# Sends a notification about the email received
def triggerNotification(emailData, service):
    toOpen = 'https://github.com/Qgiv/Secure/pulls'

    # Not currently used, but if you want to skip a message, you can set this to true
    # like if you wanted to ignore messageText containing a certain string, etc
    skipTrigger = False

    for data in emailData['payload']["parts"]:

        if (data.has_key('body') and data['body'].has_key('data') and (len(data['body']['data'])) > 0):
            # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770
            # apparently there's no padding in certain cases, so we need to add it in
            # we can add arbitrary padding length in, it'll ignore the rest of it.
            toDecode = data['body']['data'] + '======================='

            try:
                # Parse body text
                messageText = base64.b64decode(toDecode)
            except:
                e = sys.exc_info()[1]
                print(e)

            strPos = messageText.find("You are receiving this because you")

            if strPos != -1:
                subMessageText = messageText[strPos:(len(messageText))]

                # https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string
                url = re.search('(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', subMessageText)

                if url:
                    # Overriding our default URL with a more email-specific URL
                    # We're assuming the URL is the very first one we run into
                    toOpen = url.group(0)

    labelToRemove = {
        "removeLabelIds": [
            'UNREAD'
        ],
        "addLabelIds": []
    }
    
    if not skipTrigger:
        try:
            # Remove unread label
            service.users().messages().modify(userId='me', id=emailData['id'], body=labelToRemove).execute()
        except:
            pass

        # Send a user notification
        pync.notify(emailData['snippet'], title='Github Notification', appIcon='https://github.githubassets.com/images/modules/logos_page/Octocat.png', open=toOpen)        

# Main function
def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'googleCredentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        labelId = ''

        for label in labels:
            if label['name'] == 'GithubNotifications':
                labelId = label['id']
                break

        emails = getMessages(labelId, service)

        for email in emails:
            try:
                # Get email information
                emailData = service.users().messages().get(userId='me', id=email['id']).execute()
                # Trigger a notification on the email
                triggerNotification(emailData, service)
            except:
                continue

if __name__ == '__main__':
    main()