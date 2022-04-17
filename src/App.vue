<template>
  <v-app>
    <v-main>
      <NavBar>
        <v-container>
          <v-row>
            <v-col>
              <HelloWorld />
            </v-col>
            <v-col> </v-col>
          </v-row> </v-container
      ></NavBar>
    </v-main>
  </v-app>
</template>

<script>
import HelloWorld from "./components/HelloWorld.vue";
import NavBar from "./components/NavBar.vue";

export default {
  name: "App",

  components: {
    HelloWorld,
    NavBar,
  },

  data: () => ({
    //
  }),
};
</script>
