const express     = require('express');
const path     = require('path');
const ffmpegPath  = require('ffmpeg-static');
Stream            = require('node-rtsp-stream');
const {spawn} = require('child_process');


let app = express();

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.listen(5000, () => {
  console.log(`Example app listening`)
})

app.get('/', (req, res) => res.sendFile(path.join(__dirname, '../../client/public/index.html')))
app.get('/test', function(req, res){
    res.send({"Server":"Running"});
});

app.get('/query', function(req, res){

  var script_response = ""
  const script_process = spawn('python', ['test.py']);
  script_process.stdout.on('data', function (data) {
    console.log('Pipe data from python script ...');
    script_response = data.toString();
  });
    res.send({"Server":script_response});
});


app.get('/query2', function(req, res){

  var script_response = "";
  const script_process = spawn('bean-query',["beans/alex.beancount", "select sum(cost(position)) as total, month, year where account ~ \"Expenses:Consumption.*\" and not account ~\".*Tax.*\"  and year=2021 group by year, month order by year, month DESC"]);
  script_process.stdout.on("data", data => {
      res.send({"Server":data.toString()});
  });
  
});
app.get('/accounts', function(req, res){

  var script_response = "";
  const script_process = spawn('bean-query',["beans/alex.beancount", 'select account where account ~ "Expenses:Consumption.*" group by account']);
  script_process.stdout.on("data", data => {
      res.send({"Server":data.toString()});
  });

});

// Handle stop signals
const exitfn = function () {
    process.exit(0);
};
process.on("SIGINT", exitfn);
process.on("SIGTERM", exitfn);