<template>
  <v-layout style="height: 100%">
    <ViewBar :view="view"></ViewBar>

    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      @click.stop="rail = !rail"
      app
      clipped
    >
      <v-list-item prepend-icon="mdi-finance"><i>Beancounter</i></v-list-item>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          prepend-icon="mdi-folder-multiple-plus-outline"
          title="Categorize"
          @click="UpdateView('categorize')"
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-account"
          title="Overview"
          @click="$emit('view', 'overview')"
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-account-group-outline"
          title="Users"
          @click="$emit('view', 'uesrs')"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <slot></slot>
    </v-main>
  </v-layout>
</template>
<script>
import ViewBar from "./ViewBar.vue";

export default {
  name: "NavBar",
  emits: ["view"],
  components: { ViewBar },
  data() {
    return {
      drawer: true,
      items: [
        { title: "Home", icon: "mdi-home-city" },
        { title: "My Account", icon: "mdi-account" },
        { title: "Users", icon: "mdi-account-group-outline" },
      ],
      rail: true,
      view: "home",
    };
  },
  mounted: function () {
    this.$nextTick(function () {
      window.setInterval(() => {
        this.HideBar();
      }, 10000);
    });
  },
  methods: {
    HideBar: function () {
      //this.rail = true;
      console.log("foo!");
    },
    UpdateView: function (value) {
      this.$emit("view", value);
      this.view = value;
    },
  },
};

//mdi-bank-transfer-in for imports
//mdi-chart-pie
//mdi-chart-timeline-variant-shimmer
//mdi-chart-tree

//mdi-chart-scatter-plot-hexbin
//mdi-folder-multiple-plus-outline
//mdi-tab-search

//https://pictogrammers.github.io/@mdi/font/6.5.95/
</script>
