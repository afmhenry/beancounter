<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col>
            <HelloWorld/>
          </v-col>
          <v-col>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'

export default {
  name: 'App',

  components: {
    HelloWorld,
  },

  data: () => ({
    //
  }),
}
</script>
