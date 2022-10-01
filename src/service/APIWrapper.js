/* eslint-disable */
import axios from "axios";

const client = axios.create({
    baseURL: "http://localhost:5000",
    timeout: 5000,
});

const operations = {

    //invokes script file
    InvokeScript: async function (action) {
        const response = await client
            .post(`/categorize/run/${action}`)
            .then((result) => result.data);
        return response;
    },

    //Requests all accounts in the beancount file, 
    //Returns them in array
    GetAccounts: async function (params) {

        const response = await client
            .get(`/accounts${HandleParams(params)}`)
            .then((result) => result.data);
        return response;
    },


    GetSpending: async function (params) {
        const response = await client
            .get(`/hist${HandleParams(params)}`)
            .then((result) => result.data);
        return response;
    },

    //updates json file containing mappings
    SendUpdatedCategories: async function (categorized) {
        const response = await client
            .post(`/categorized`, categorized)
            .then((result) => result.data);
        return response;
    },

    //updates json file containing mappings
    UploadStatementFile: async function (files) {
        console.log(typeof files)
        console.log(files)
        const headers = { 'Content-Type': "multipart/form-data" };
        const response = await client.post('/statements', files, { headers }).then((res) => {
            res.data
        });
        return response
    }

}

function HandleParams(params) {
    var parsed_params = ""
    if (params) {
        parsed_params = "?"
        for (var i in params) {
            parsed_params += params[i] + "&"
        }
    }
    return parsed_params
}

export default operations