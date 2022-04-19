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
        console.log(response)
        return response;
    },
    GetAccounts: async function () {
        const response = await client
            .get(`/accounts`)
            .then((result) => result.data);
        console.log(response)
        return response;
    }
}

export default operations