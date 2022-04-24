<template>
  <v-container>
    <div style="text-align: center">
      <h1>Import New Banking Statements</h1>
      <br />
    </div>

    <v-card>
      <v-file-input ref="file" type="file" label="File input"></v-file-input>
      <div style="text-align: center" class="py-5">
        <v-btn color="secondary" @click="UploadFile">Upload</v-btn>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import operations from "../service/APIWrapper";

export default {
  name: "ImportModule",

  data: () => ({
    files: null,
  }),

  watch: {},
  methods: {
    UploadFile() {
      this.files = this.$refs.file.files;

      operations.UploadStatementFile(this.files).then((response) => {
        console.log(response); 
      });
    },
  },
};
</script>
