import express from 'express';
import path from 'path';
import bodyParser from 'body-parser';
import cron from 'node-cron';
import { exec } from 'child_process';
import async from 'async';
import fs from 'fs';
import * as admin from 'firebase-admin';
import * as serviceAccount from '/home/john/tfdg-server/config/firebase-admin.json';

// init service account sdk admin
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://tfdg-175615.firebaseio.com/'
});

const db = admin.database();
const homepageRef = db.ref('/homepage');
const configRef = db.ref('/config');

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

app.use(express.static('/home/john/dist'));

app.post('/driveCallback', (req, res) => {
  console.log('update received, running scripts');
  async.series([grabData, importData]);
  res.sendStatus(200);
});

app.get('*', (req, res) => {
  res.sendFile('/home/john/dist/index.html');
});

// uncomment for production
async.series([grabData, importData]);

// call setupWatch once, and then start a cron job to run it every 2 minutes.
setupWatch();

const task = cron.schedule('0 1,13 * * *', () => {
  console.log('stopping old watch and starting a new one');
  setupWatch();
});
task.start();

app.listen(8080, () => {
  console.log('app is listening');
});

function grabData(cb) {
  exec('/home/john/tfdg-server/parser/getDrive.py', (err, stdout, stderr) => {
    if (err) {
      console.log('error running getDrive.py');
    }
    cb(null);
  });
}

function importData(cb) {
  fs.readFile('/home/john/tfdg-server/parser/homepage.json', 'utf-8', (err, data) => {
    homepageRef.set(JSON.parse(data));
  });
}

function setupWatch() {
  exec('/home/john/tfdg-server/server/setupWatch.py', (err, stdout, stderr) => {
    if (err) {
      console.log('error running setupWatch.py');
    }
  });
}
