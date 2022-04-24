<template>
  <v-layout fill-height style="height: 100vh">
    <ViewBar :view="view"></ViewBar>
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      app
      clipped
      width="170"
      rail-width="72"
    >
      <v-list density="compact" nav>
        <v-list-item
          v-for="item in items"
          :key="item.name"
          :prepend-icon="item.icon"
          :title="item.title"
          @click="UpdateView(item.title)"
          :class="{
            'v-list-item--active text-primary': this.view === item.title,
          }"
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
        { title: "Import", icon: "mdi-database-import" },
        { title: "Categorize", icon: "mdi-folder-multiple-plus-outline" },
        { title: "Overview", icon: "mdi-account" },
        { title: "Users", icon: "mdi-account-group-outline" },
      ],
      rail: true,
      view: "home",
      isActive: null,
    };
  },
  methods: {
    HideBar: function () {
      this.rail = true;
      console.log("foo!");
    },
    UpdateView: function (value) {
      this.$emit("view", value);
      if (value === this.view || this.rail === true) {
        this.rail = !this.rail;
      }
      this.view = value;
    },
    toggleItem(index) {
      this.isActive = index;
    },
  },
};

//mdi-database-import
//mdi-bank-transfer-in for imports
//mdi-chart-pie
//mdi-chart-timeline-variant-shimmer
//mdi-chart-tree

//mdi-chart-scatter-plot-hexbin
//mdi-folder-multiple-plus-outline
//mdi-tab-search

//https://pictogrammers.github.io/@mdi/font/6.5.95/
</script>
