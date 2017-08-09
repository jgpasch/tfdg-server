#!/usr/bin/python3

from __future__ import print_function
import httplib2
import os
import io
import datetime
import csv
import json
import requests

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaIoBaseDownload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/tfdg-drive-api-creds.json
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
home_dir = os.path.expanduser('~')
# secret_file = os.path.join(home_dir, 'py3-drive', 'src', 'quickstart.py')

# CLIENT_SECRET_FILE = secret_file
CLIENT_SECRET_FILE = '/home/john/tfdg-server/config/client_secret.json'
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
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def parseFile():
  # the team names are 3 columns apart
  offset = 3
  # the first team names starts at the 3rd position (index 2)
  tn_start = 2
  # the first league points score starts at index 3
  lp_start = 3

  ###########################################################
  # open the homepage file fo reading and read it into csv
  f = open('/home/john/tfdg-server/parser/data.csv', 'r')
  reader = csv.reader(f)

  # setup dict to hold homepage data
  team_info = {}

  # grab the first 3 lines for 1) team names 2) managers 3) league points
  team_names = next(reader)
  mr_manager = next(reader)
  lp = next(reader)


  # grab each of the 8 team names
  # and create new dict entries for them
  for i in range(8):
    # index for team name
    tn_ind = tn_start + (offset * i)
    # index for lp so far
    lp_ind = lp_start + (offset * i)
    team_info[team_names[tn_ind]] = { 'manager': mr_manager[tn_ind] ,'lp': lp[lp_ind] }

  # create a new json file to be imported into firebase
  write_to_json = open('/home/john/tfdg-server/parser/homepage.json', 'w')
  write_to_json.write(json.dumps(team_info))

  # close files
  f.close()
  write_to_json.close()


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    firebase_url = 'https://tfdg-175615.firebaseio.com/config.json'

    result = requests.get(firebase_url)

    file_id = result.json()['file_id']

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    request = service.files().export_media(fileId=file_id, mimeType='text/csv')
    d = datetime.datetime.now()
    filename = '/home/john/tfdg-server/parser/data.csv'
    fh = io.FileIO(filename, mode='wb')
    downloader  = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    parseFile()

if __name__ == '__main__':
    main()
