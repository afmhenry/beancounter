<template>
  <v-app-bar app clipped-left>
    <h1>{{ view }}</h1>
  </v-app-bar>
</template>

<script>
export default {
  name: "ViewBar",
  props: ["view"],
  data: () => ({}),
};
</script>
