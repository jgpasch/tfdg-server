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
from firebase import firebase

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

CLIENT_SECRET_FILE = '/home/john/tfdg-server/config/client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
APPLICATION_NAME = 'Drive API Python Quickstart'

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

def removeOldWatch(http):
  firebase_url = 'https://tfdg-175615.firebaseio.com/config/watchResponse.json'
  result = requests.get(firebase_url)
  res = result.json()

  try:
    channelId = res['channelId']
    resourceId = res['resourceId']
    address = res['address']
    resourceUri = res['resourceUri']
    kind = res['kind']
    myType = res['type']
  except KeyError:
    f = open('/home/john/tfdg-server/server/stopResponse.txt', 'a')
    f.write('\n\n')
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
    f.write('error making http stop request to channels')
    f.close()
    return

  # worked as intended, print response to file - should be empty string if it worked
  f = open('/home/john/tfdg-server/server/stopResponse.txt', 'a')
  f.write('\n\n')
  f.write(json.dumps(res))
  f.close()

def main():
  global firebase
  firebase_url = 'https://tfdg-175615.firebaseio.com'
  config_url = firebase_url + '/config.json'
  firebase = firebase.FirebaseApplication(firebase_url, None)

  result = requests.get(config_url)
  file_id = result.json()['file_id']

  now = time.time() * 1000
  expiration = int(now) + (3600000 * 13)
  # expiration = int(now) + 70000

  data = { "id": str(uuid.uuid4()),
           "type": "web_hook",
           "address": "https://bigspender.info/driveCallback",
           "expiration": expiration }

  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())

  # remove old watcher _ channel => stop
  removeOldWatch(http)

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
    'address': 'https://bigspender.info/driveCallback',
    'kind': 'api#channel',
    'type': 'web_hook',
    'resourceUri': res['resourceUri'],
    'expiration': res['expiration']
  }
  firebase.put('/config', data=data, name="watchResponse")

if __name__ == '__main__':
  main()
