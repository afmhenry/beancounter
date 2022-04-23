<template>
  <v-app fill-height>
    <v-main>
      <NavBar @view="SelectView">
        <v-container style="margin: 0px 10px">
          <CategorizeModule
            v-if="this.view === 'Categorize'"
          ></CategorizeModule>
        </v-container>
      </NavBar>
    </v-main>
  </v-app>
</template>

<script>
import CategorizeModule from "./components/CategorizeModule.vue";
import NavBar from "./components/NavBar.vue";

export default {
  name: "App",

  components: {
    CategorizeModule,
    NavBar,
  },

  data: () => ({
    view: "Categorize",
  }),
  methods: {
    SelectView: function (value) {
      this.view = value;
    },
  },
};
</script>
