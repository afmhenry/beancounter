/* eslint-disable */
import express from 'express';
import BodyParser from 'body-parser';
import { spawn, exec } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import FileReader from "filereader";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
//todo: make this path a UI config
const file = __dirname + '/../../data/mapping-private.json';

let app = express();
let port = 5000

var timeout = 100000;
var categorize = null

app.use(BodyParser.json());

app.listen(port, () => {
    console.log(`Express listening on port ${port}`)
})

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

//get monthly breakdown of certain accounts
app.get('/hist', function (req, res) {
    BqlHandler.SendRequest(req, res)
});


//provide list of accounts, matching the params
app.get('/accounts', function (req, res) {
    BqlHandler.SendRequest(req, res)
});


//Category API's
app.post('/categorize/these', function (req, res) {

    categorize = req.body.message;
    res.send({ "status": "recieved" })
});

app.post('/categorize/run/*', function (req, res) {
    CategoryHandler.SpawnChildProcess(req.path.split("/")[3], res);
});
app.post('/categorized', function (req, res) {
    CategoryHandler.UpdateJSONMapping(req.body, res)
});


//not easy to get the file...will have to eval if express/js is right tool for that. 
//maybe will be the pushing point for moving to flask. 
//could also invoke a cli copy, but that ofc could only work on non-windows. 
app.post('/statements', function (req, res) {
    console.log(req)

    res.send({ "status": "recieved" })
});


// Handle stop signals
const exitfn = function () {
    process.exit(0);
};
process.on("SIGINT", exitfn);
process.on("SIGTERM", exitfn);

//dfancy timeout logic, so if it stalls, we get an error. 
function getAllCategories(timeout) {

    var start = Date.now();
    return new Promise(waitForResponse);

    function waitForResponse(resolve, reject) {

        if (categorize !== null) {
            resolve(categorize)
        } else if (timeout && (Date.now() - start) >= timeout) {
            reject(new Error("timeout"));
        } else
            setTimeout(waitForResponse.bind(this, resolve, reject), 30);
    }
}

//todo: move this to separate file...but do it well. 

const BqlHandler = {
    //MORE query formats here...may need to re-org. http://aumayr.github.io/beancount-sql-queries/
    SendRequest: (req, res) => {
        console.log("Request: params-", req.params, " query-", req.query)
        var bql = BqlHandler.CreateBQLQuery(req);
        console.log("Query: ", bql.args[2].toString())
        var script_process = spawn(bql.cmd, bql.args);
        var output = "";
        script_process.stdout.setEncoding('utf8');


        //catch if it fails...rare, error may manifest in response instead. 
        //so some of that is handled in the RespToJson too. 
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
            return
        });
    },

    //parse command, and execute bql query as child process 
    CreateBQLQuery: (req) => {
        var bql = {
            "cmd": 'bean-query',
            "args": ["-f=csv", "beans/alex.beancount"]
        }
        //apply operations from path
        var bql_base = BqlHandler.PathToBql(req.path);

        //apply operations from query params, as filters
        var bql_with_filter = BqlHandler.FilterToBql(req.query, bql_base);
        bql["args"].push(bql_with_filter)

        return bql;
    },

    //convert the path parameters into the relevant section of a bql statement
    PathToBql: (paths) => {
        var query = ""
        switch (paths.split("/")[1]) {
            case "accounts":
                if (paths.length == 2) {
                    query = "select account";
                    //get info on certain account
                } else {
                    //return all accounts
                    query = "select account <FILTER> group by account";
                }
                break;
            case "hist":
                //query = "select sum(position) as total, year, month <FILTER> group by year, month"
                query = "SELECT year, month, account, sum(position) as total <FILTER> group by year,month, account "
                break;
        }
        return query;
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

    //convert the  bql to json for FE consumption
    RespToJson: (bql_string) => {
        try {
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
                    if (keys.length === 1 && keys[0] === "account") {
                        values.push(line.trim())
                    } else {
                        var temp = {}
                        line.split(",").forEach(function (entry, j) {

                            temp[keys[j]] = entry.trim()
                        });
                        values[i - 1] = temp;
                    }
                }
            });
            return values;
        } catch (error) {
            console.log("Process output invalid", bql_string, error)
        }

    },
}

const CategoryHandler = {
    SpawnChildProcess: (script, res) => {
        try {
            var script_process = spawn("./scripts/" + script + ".sh")
            console.log(script)
            script_process.on('error', (err) => {
                console.error('Failed to start subprocess.', err);
            });

            //send when stdout is done
            script_process.stdout.on("close", data => {

                //how do I want to handle output from the different scripts? 
                //can i make this a more generic structure?
                //probably can move this part out and do conditions on which script is invoked. 
                getAllCategories(timeout).then(() => {
                    res.send({
                        "message": "success",
                        "content": "categorize",
                        "values": categorize
                    })
                    categorize = []
                    return
                }).catch(error => {
                    console.error("Timeout on categorize", error)
                    res.send(500, {
                        "message": "failed",
                    })
                })
            });

        } catch (error) {
            console.error("category", error)
            return res.send({ "message": "failed" })
        }
    },
    UpdateJSONMapping: (contents, res) => {

        const content = 'Some content!'

        var parsedNewCats = {}
        for (var i in contents) {
            parsedNewCats[contents[i].name] = contents[i].category
        }
        fs.readFile(file, 'utf-8', (error, content) => {
            if (error) {
                console.error("Error reading: ", file, error)
                return res.send(500, {
                    "message": "failed",
                })
            } else
                if (content) {
                    var categories = JSON.parse(content)
                    const mergedObject = {
                        ...categories,
                        ...parsedNewCats
                    };
                    fs.writeFile(file, JSON.stringify(mergedObject, null, 2), err => {
                        if (err) {
                            console.error("Error writing: ", file, err)
                            return res.send(500, {
                                "message": "failed",
                            })
                        } else {
                            return res.send({
                                "message": "success",
                            })
                        }
                    })
                }

        })

    }
}
