<template>
  <v-app fill-height>
    <v-main>
      <NavBar @view="SelectView">
        <v-container style="margin: 0px 10px">
          <ImportModule v-if="this.view === 'Import'"></ImportModule>

          <HomeModule v-if="this.view === 'Home'"></HomeModule>
          <CategorizeModule
            v-if="this.view === 'Categorize'"
          ></CategorizeModule>
          <DashboardModule v-if="this.view === 'Dashboard'"></DashboardModule>
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
import DashboardModule from "./components/DashboardModule.vue";

export default {
  name: "App",

  components: {
    HomeModule,
    CategorizeModule,
    NavBar,
    ImportModule,
    DashboardModule,
  },

  data: () => ({
    view: "Dashboard",
  }),
  methods: {
    SelectView: function (value) {
      this.view = value;
    },
  },
};
</script>
