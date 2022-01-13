// api.js

module.exports = {

    BqlToJson : function(bql_string){
        lines = bql_string.split(/\r?\n/);
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