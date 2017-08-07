import express from 'express';
import path from 'path';
import bodyParser from 'body-parser';

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

app.use(express.static('/Users/john/github/tfdg/dist'));

app.get('*', (req, res) => {
  res.sendFile('/Users/john/github/tfdg/dist/index.html');
});


app.listen(8080, () => {
  console.log('app is listening');
});