#!/usr/bin/python3

import os
import json
import requests
from apiclient import discovery
from oauth2client.file import Storage
from oauth2client import client
from oauth2client import tools
import httplib2
import uuid
import time
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

CLIENT_SECRET_FILE = '/home/john/tfdg-server/config/client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
APPLICATION_NAME = 'Drive API Python Quickstart'
OLD_FILE_ID = ''

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = '/home/john/.credentials'
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'tfdg-drive-api-creds.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        print('im insdie here')
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def removeOldWatch(http, configRes):
  res = configRes['watchResponse']
  print(res)

  try:
    if not OLD_FILE_ID:
      channelId = res['channelId']
    else:
      channelId = OLD_FILE_ID
    resourceId = res['resourceId']
    address = res['address']
    resourceUri = res['resourceUri']
    kind = res['kind']
    myType = res['type']
  except KeyError:
    f = open('/home/john/tfdg-server/server/stopResponse.txt', 'a')
    f.write('\n\n')
    f.write(datetime.datetime.now().strftime("%m/%d/%y - %H:%M\t"))
    f.write('key error, abandoning stop response')
    f.close()
    return

  service = discovery.build('drive', 'v3', http=http)

  body = {
    'id': channelId,
    'resourceId': resourceId,
    'address': address,
    'resourceUri': resourceUri,
    'kind': kind,
    'type': myType
  }

  try:
    res = service.channels().stop(body=body).execute()
  except:
    f = open('/home/john/tfdg-server/server/stopResponse.txt', 'a')
    f.write('\n\n')
    f.write(datetime.datetime.now().strftime("%m/%d/%y - %H:%M\t"))
    f.write('error making http stop request to channels')
    f.close()
    return

  # worked as intended, print response to file - should be empty string if it worked
  f = open('/home/john/tfdg-server/server/stopResponse.txt', 'a')
  f.write('\n\n')
  f.write(datetime.datetime.now().strftime("%m/%d/%y - %H:%M\t"))
  f.write(json.dumps(res))
  f.close()

def main():
  # setup admin service account for authorized writing to DB
  global credentials
  cred = credentials.Certificate('/home/john/tfdg-server/config/firebase-admin.json')
  fb_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tfdg-175615.firebaseio.com'
  })

  configRef = db.reference('/config')

  configRes = configRef.get()
  file_id = configRes['file_id']

  now = time.time() * 1000
  expiration = int(now) + (3600000 * 13)

  data = { "id": str(uuid.uuid4()),
           "type": "web_hook",
           "address": "https://bigspender.info/driveCallback",
           "expiration": expiration }

  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())

  # remove old watcher _ channel => stop
  removeOldWatch(http, configRes)

  service = discovery.build('drive', 'v3', http=http)
  res = service.files().watch(fileId=file_id, body=data).execute()

  f_write = open('/home/john/tfdg-server/server/watchResponse.txt', 'a')
  f_write.write(json.dumps(res))
  f_write.write('\n\n')
  f_write.close()

  # SAVE response from files().watch to firebase
  data = {
    'channelId': res['id'],
    'resourceId': res['resourceId'],
    'resourceUri': res['resourceUri'],
    'expiration': res['expiration']
  }
  # firebase.put('/config', data=data, name="watchResponse")
  configRef.child('watchResponse').update(data)

  # save old channel id for when the file id changes in firebase
  OLD_FILE_ID = res['id']

if __name__ == '__main__':
  main()
