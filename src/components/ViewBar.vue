<template>
  <v-app-bar app clipped-left style="padding: 0px 0px">
    <v-list-item prepend-icon="mdi-finance" floating
      ><i><h1>Beancounter</h1></i></v-list-item
    >
    <h2 color="secondary">{{ view }}</h2>
  </v-app-bar>
</template>

<script>
export default {
  name: "ViewBar",
  props: ["view"],
  data: () => ({}),
};
</script>
