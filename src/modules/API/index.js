
//Todo: extend to support all types of queries
const Helpers = {
    RequestData: (info) => {
        console.log(info)
        console.log(new URLSearchParams(info).toString)
        fetch("/v1/accounts?"+new URLSearchParams(info),
        {
            "method": "GET"
        }
        ).then(function (response) {
            if (response.ok) {
                response.json().then(function (responseJson) {
                    console.log(responseJson);
                    return responseJson;
                }); 
            }
        }).catch(function (error) {
            console.error(error);
        });
      return "foo"
    }
}


export default Helpers
