// api.js
const {spawn}   = require('child_process');

var BqlHandler = {

    Create: function(req){
        console.log(req.params);
        bql =  {
            "cmd":'bean-query', 
            "args": ["-f=csv","beans/alex.beancount"]
        }
        //apply operations from path
        bql_base = BqlHandler.PathToBql(req.params);
        //apply operations from query params, as filters
        bql_with_filter = BqlHandler.FilterToBql(req.query, bql_base);

        bql["args"].push(bql_with_filter)

        return bql;
    },
    //convert the query parameters into the relevant section of a bql statement
    FilterToBql: function(queries, bql_base){
        filter = ""
        if(Object.keys(queries) !== 0){
            filter = "where";
            for(var key in queries){
                modifier = ""
    
                switch(key){
                    case "FromDate":
                        break
                    case "ToDate":
                        break
                    case "Exclude":
                        modifier = " not"
                    case "Include":
                        query_values = queries[key].split(",")
                        for(var part in query_values){
                            filter  += modifier+" account ~'.*"+query_values[part]+".*' "
                            if(part != query_values.length-1){
                                filter += "and"
                            }
                        }
                        break
                }
                delete queries[key]
    
                if(Object.keys(queries).length !== 0){
                    filter += "and"
                }
            }
        }
        return bql_base.replace("\<FILTER\> ", filter)
    },
    //convert the path parameters into the relevant section of a bql statement
    PathToBql: function(paths){
        query = ""
        switch(paths[0]){
            case "accounts":
                if(paths.length == 2){
                    query = "select account";
                    //get info on certain account
                }else{
                    //return all accounts
                    query = "select account <FILTER> group by account";
                }
            case "balances":
                if(paths.length == 2){
                    //get balance on certain account
                }else{
                    //get balance on all accounts
                }
        }
        return query;
    },
    //convert the 
        //bql to json for FE consumption
    RespToJson: function(bql_string){
        lines = bql_string.toString().split(/\r?\n/);
        keys = []
        values = []
        lines.forEach(function(line, i){
            if(i === 0){
                keys= line.split(",");
            }else if(line){
                temp = {}
                line.split(",").forEach(function(entry, j){
                    temp[keys[j]] =  entry.trim()
                });
                values[i-1] = temp;
            }
        });
        return values;
    }
}


module.exports = {
    SendRequest: function(req,res){
        bql = BqlHandler.Create(req);
        console.log(bql)
        const script_process = spawn(bql.cmd,bql.args);

        script_process.on('error', (err) => {
            console.error('Failed to start subprocess.', err);
          });
          
        script_process.stdout.on("data", data => {
            res.send(BqlHandler.RespToJson(data));
        });
    }
}
    

