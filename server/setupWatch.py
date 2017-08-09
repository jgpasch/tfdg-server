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

def main():
  firebase_url = 'https://tfdg-175615.firebaseio.com/config.json'
  result = requests.get(firebase_url)
  file_id = result.json()['file_id']

  now = time.time() * 1000
  # tomorrow = int(now) + 86000000
  expiration = int(now) + 120000

  data = { "id": str(uuid.uuid4()),
           "type": "web_hook",
           "address": "https://bigspender.info/driveCallback",
           "expiration": expiration }

  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())

  service = discovery.build('drive', 'v3', http=http)
  res = service.files().watch(fileId=file_id, body=data).execute()

  f_write = open('/home/john/tfdg-server/server/watchResponse.txt', 'w')
  f_write.write(json.dumps(res))
  f_write.close()

if __name__ == '__main__':
  main()