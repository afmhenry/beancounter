
//Todo: extend to support all types of queries
const Helpers = {
    RequestData: async (info) => {
        const response = await fetch("/v1/positions?"+new URLSearchParams(info),{"method": "GET"})
        const response_obj = await response.json();
        return response_obj;
    }
}

export default Helpers
