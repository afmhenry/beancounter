<template>
  <v-app fill-height>
    <v-main>
      <NavBar @view="SelectView">
        <v-container style="margin: 0px 10px">
          <HomeModule v-if="this.view === 'Home'"></HomeModule>
          <CategorizeModule
            v-if="this.view === 'Categorize'"
          ></CategorizeModule>
          <ImportModule v-if="this.view === 'Import'"></ImportModule>
        </v-container>
      </NavBar>
    </v-main>
  </v-app>
</template>

<script>
import HomeModule from "./components/HomeModule.vue";
import CategorizeModule from "./components/CategorizeModule.vue";
import NavBar from "./components/NavBar.vue";
import ImportModule from "./components/ImportModule.vue";

export default {
  name: "App",

  components: {
    HomeModule,
    CategorizeModule,
    NavBar,
    ImportModule,
  },

  data: () => ({
    view: "Home",
  }),
  methods: {
    SelectView: function (value) {
      this.view = value;
    },
  },
};
</script>
