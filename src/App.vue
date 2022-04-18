<template>
  <v-app class="fill-height" style="height: 100vh">
    <v-main style="height: 100vh">

      <NavBar @view="SelectView">
        <v-container style="height: 100vh; margin: 0px 10px">
          <Categorize v-if="this.view === 'categorize'"></Categorize>
        </v-container>
      </NavBar>
    </v-main>
  </v-app>
</template>

<script>
import Categorize from "./components/Categorize.vue";
import NavBar from "./components/NavBar.vue";
import ViewBar from "./components/ViewBar.vue";

export default {
  name: "App",

  components: {
    Categorize,
    NavBar,
    ViewBar,
  },

  data: () => ({
    view: "categorize",
  }),
  methods: {
    SelectView: function (value) {
      this.view = value;
    },
  },
};
</script>
