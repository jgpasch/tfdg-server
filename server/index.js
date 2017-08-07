import express from 'express';
import path from 'path';
import bodyParser from 'body-parser';

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

app.use(express.static('/home/john/dist'));

app.get('*', (req, res) => {
  res.sendFile('/home/john/dist/index.html');
});


app.listen(8080, () => {
  console.log('app is listening');
});