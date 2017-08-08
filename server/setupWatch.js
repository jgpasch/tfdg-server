import fs from 'fs';
import readline from 'readline';
import google from 'googleapis';
import googleAuth from 'google-auth-library';

const SCOPES = ['https://www.googleapis.com/auth/drive'];

fs.readFile('/home/john/tfdg-server/config/client_secret.json', (err, content) => {
  if(err) {
    console.log('error loading client secret file ', + err);
    return;
  }
  authorize(JSON.parse(content), getFile)
});

/**
 * Create an OAuth2 client with the given credentials, and then execute the
 * given callback function.
 *
 * @param {Object} credentials The authorization client credentials.
 * @param {function} callback The callback to call with the authorized client.
 */
function authorize(creds, cb) {
  const clientSecret = credentials.installed.client_secret;
  const clientId = credentials.installed.client_id;
  const redirectUrl = credentials.installed.redirect_uris[0];
  const auth = new googleAuth();
  const oauth2Client = new auth.OAuth2(clientId, clientSecret, redirectUrl);

  getNewToken(oauth2Client, cb);
}

/**
 * Get and store new token after prompting for user authorization, and then
 * execute the given callback with the authorized OAuth2 client.
 *
 * @param {google.auth.OAuth2} oauth2Client The OAuth2 client to get token for.
 * @param {getEventsCallback} callback The callback to call with the authorized
 *     client.
 */
function getNewToken(oauth2Client, callback) {
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scopes: SCOPES
  });
}