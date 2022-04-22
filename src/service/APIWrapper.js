import axios from "axios";
const client = axios.create({
    baseURL: "http://localhost:5000",
    timeout: 5000,
});

const operations = {
    RunCategorize: async function () {
        const response = await client
            .post(`/categorize/run`)
            .then((result) => result.data);
        return response;
    },
    GetAccounts: async function (params) {
        var path = `/accounts`
        if (params) {
            path += "?" + params
        }
        const response = await client
            .get(path)
            .then((result) => result.data);
        return response;
    }
}

export default operations