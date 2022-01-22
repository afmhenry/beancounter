
//Todo: extend to support all types of queries
const Helpers = {
    RequestData: async (info) => {
        console.log(info)
        const response = await fetch("/v1/positions?"+new URLSearchParams(info),{"method": "GET"})
        const response_obj = await response.json();
        return response_obj;
        /* then(function (response) {
            if (response.ok) {
                response.json().then(function (responseJson) {
                    console.log(responseJson);
                    console.log("done")
                    return responseJson;
                });
            }
        }).catch(function (error) {
            console.error(error);
        });
      return "foo" */
    }
}


export default Helpers
