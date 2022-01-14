// api.js

module.exports = {

    BqlToJson : function(bql_string){
        var lines = bql_string.split(/\r?\n/);
        var keys = []
        var values = []
        lines.forEach(function(line, i){
            if(i === 0){
                keys= line.split(",");
            }else if(line){
                var temp = {}
                line.split(",").forEach(function(entry, j){
                    temp[keys[j]] =  entry.trim()
                });
                values[i-1] = temp;
            }
        });
        
        return values;
    }

}