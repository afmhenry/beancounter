const express   = require('express');
const path      = require('path');
var api         = require('./api');
const BodyParser = require('body-parser');


let app = express();

app.use(BodyParser.json());

app.listen(5000, () => {
  console.log(`Example app listening`)
})

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});


app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')))

//  const script_process = spawn('bean-query',["-f=csv","beans/alex.beancount", "select sum(cost(position)) as total, month, year where account ~ \"Expenses:Consumption.*\" and not account ~\".*Tax.*\"  and year=2021 group by year, month order by year, month DESC"]);


app.get('/v1/*', function(req, res){
  console.log(typeof res)
  api.SendRequest(req,res)
});


// Handle stop signals
const exitfn = function () {
    process.exit(0);
};
process.on("SIGINT", exitfn);
process.on("SIGTERM", exitfn);