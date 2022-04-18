<template>
  <v-container>
    <h1 @click="RunCategorize">Categorize</h1>

    <v-card> </v-card>
  </v-container>
</template>

<script>
import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:5000",
  timeout: 5000,
});

export default {
  name: "HelloWorld",

  data: () => ({}),
  methods: {
    RunCategorize: function () {
      client.post(`/categorize/run`).then((result) => result.data);
    },
  },
};
</script>
