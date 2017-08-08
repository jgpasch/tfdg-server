import express from 'express';
import path from 'path';
import bodyParser from 'body-parser';
import cron from 'node-cron';
import { exec } from 'child_process';
import async from 'async';

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


app.listen(8080, () => {
  console.log('app is listening');
});

function grabData() {
  exec('/home/john/py-parser/getDrive.py', (err, stdout, stderr) => {
    if (err) {
      console.log('error running getDrive.py');
    }
  });
}

function importData() {
  exec('/home/john/.nvm/versions/node/v8.2.1/bin/node /home/john/.nvm/versions/node/v8.2.1/lib/node_modules/firebase-import/bin/firebase-import.js --database_url https://tfdg-175615.firebaseio.com --json /home/john/py-parser/homepage.json --path /homepage --force', (err, stdout, stderr) => {
    if (err) {
      console.log('error running import data');
    }
  });
}
