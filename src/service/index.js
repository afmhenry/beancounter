import express from 'express';
import BodyParser from 'body-parser';
import { spawn } from 'child_process';

//import getOpenapiService from "./services/openapiService";

let app = express();
let port = 5000

app.use(BodyParser.json());

app.listen(port, () => {
    console.log(`Express listening on port ${port}`)
})
app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

app.get('/*', function (req, res) {
    console.log(typeof res)
    SendRequest(req,res)
});


// Handle stop signals
const exitfn = function () {
    process.exit(0);
};
process.on("SIGINT", exitfn);
process.on("SIGTERM", exitfn);


//todo: move this to separate file...but well. 

const BqlHandler = {
    //MORE query formats here...may need to re-org. http://aumayr.github.io/beancount-sql-queries/

    SpawnChildProcess: (req) => {
        var bql = {
            "cmd": 'bean-query',
            "args": ["-f=csv", "../beancounter/beans/alex.beancount"]
        }
        //apply operations from path
        var bql_base = BqlHandler.PathToBql(req.params);
        //apply operations from query params, as filters
        var bql_with_filter = BqlHandler.FilterToBql(req.query, bql_base);
        bql["args"].push(bql_with_filter)

        return bql;
    },
    //convert the query parameters into the relevant section of a bql statement
    FilterToBql: (queries, bql_base) => {
        var filter = "";
        Object.keys(queries).forEach((k) => (queries[k] == "") && delete queries[k]);
        if (Object.keys(queries).length !== 0) {
            filter = "where";
            for (var key in queries) {
                var modifier = "";
                switch (key) {
                    case "Month":
                    case "Year":
                        //support multiple entries in month or year, perhaps ranges would be more elegant...
                        filter += " (" + key.toLowerCase() + "=" + queries[key].replaceAll(",", " or " + key.toLowerCase() + "=") + ") ";
                        break;
                    case "ToDate":
                        //date <= 2021-12-31
                        break;
                    case "FromDate":
                        // date  >=2021-11-01
                        break;
                    case "Exclude":
                        if (queries[key]) {
                            modifier = " not";
                        } else {
                            break;
                        }
                    case "Include":
                        //split into multiple 
                        var query_values = queries[key].split(",");
                        for (var part in query_values) {
                            filter += modifier + " account ~'.*" + query_values[part] + ".*' ";
                            if (Number(part) != query_values.length - 1) {
                                filter += "and";
                            }
                        }
                        break;
                }
                delete queries[key];

                if (Object.keys(queries).length !== 0) {
                    filter += "and";
                }
            }
        }
        var resp_bql_base = bql_base.replace("<FILTER> ", filter);
        return resp_bql_base
    },
    //convert the path parameters into the relevant section of a bql statement
    PathToBql: (paths) => {
        var query = ""
        switch (paths[0]) {
            case "accounts":
                console.log("here",paths)
                if (paths.length == 2) {
                    query = "select account";
                    //get info on certain account
                } else {
                    //return all accounts
                    query = "select account <FILTER> group by account";
                }
                break;
            case "positions":
                query = "select sum(position) as total, year, month <FILTER> group by year, month"
                break;
        }
        return query;
    },
    //convert the  bql to json for FE consumption
    RespToJson: (bql_string) => {

        var lines = bql_string.toString().split(/\r?\n/);
        var keys = []
        var values = []
        lines.forEach(function (line, i) {
            if (i === 0) {
                keys = line.split(",");
                keys.forEach(function (value, index) {
                    //might need this later.
                });
            } else if (line) {
                var temp = {}
                line.split(",").forEach(function (entry, j) {
                    temp[keys[j]] = entry.trim()
                });
                values[i - 1] = temp;
            }
        });
        return values;
    }
}


function SendRequest(req, res){
    console.log("Request: params-", req.params, " query-", req.query)
    var bql = BqlHandler.SpawnChildProcess(req);
    console.log("Query: ", bql.args[2].toString())
    var script_process = spawn(bql.cmd, bql.args);
    var output = "";
    script_process.stdout.setEncoding('utf8');

    script_process.on('error', (err) => {
        console.error('Failed to start subprocess.', err);
    });

    //gather stdout, since it could go a while
    script_process.stdout.on("data", data => {
        data = data.toString()
        output += data;
    });
    //send when stdout is done
    script_process.stdout.on("close", data => {
        console.log("Query complete, ", output.length, " rows");
        res.send(BqlHandler.RespToJson(output));
    });
}