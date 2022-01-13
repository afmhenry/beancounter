const express   = require('express');
const path      = require('path');
const {spawn}   = require('child_process');
var api         = require('./api');

let app = express();

app.listen(5000, () => {
  console.log(`Example app listening`)
})

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});


app.get('/', (req, res) => res.sendFile(path.join(__dirname, '../../react-client/public/index.html')))


app.get('/consumption', function(req, res){
  var script_response = "";
  const script_process = spawn('bean-query',["-f=csv","beans/alex.beancount", "select sum(cost(position)) as total, month, year where account ~ \"Expenses:Consumption.*\" and not account ~\".*Tax.*\"  and year=2021 group by year, month order by year, month DESC"]);
  script_process.stdout.on("data", data => {
    response = api.BqlToJson(data.toString());
    res.send(response);
  });
});

app.get('/accounts', function(req, res){
  var script_response = "";
  const script_process = spawn('bean-query',["-f=csv","beans/alex.beancount", 'select account where account ~ "Expenses:Consumption.*" group by account']);
  script_process.stdout.on("data", data => {
    response = api.BqlToJson(data.toString());
    res.send(response);
  });

});

// Handle stop signals
const exitfn = function () {
    process.exit(0);
};
process.on("SIGINT", exitfn);
process.on("SIGTERM", exitfn);