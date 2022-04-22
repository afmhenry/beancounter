<template>
  <v-app class="fill-height" style="height: 100vh">
    <v-main style="height: 100vh">
      <NavBar @view="SelectView">
        <v-container style="margin: 0px 10px">
          <CategorizeModule
            v-if="this.view === 'categorize'"
          ></CategorizeModule>
        </v-container>
      </NavBar>
    </v-main>
  </v-app>
</template>

<script>
import CategorizeModule from "./components/CategorizeModule.vue";
import NavBar from "./components/NavBar.vue";
import ViewBar from "./components/ViewBar.vue";

export default {
  name: "App",

  components: {
    CategorizeModule,
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
