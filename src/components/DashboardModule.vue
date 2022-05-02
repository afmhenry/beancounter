<template>
  <v-container fill-height>
    <div style="text-align: center">
      <h1>Dashboards</h1>
    </div>
    <v-card>
      <v-toolbar color="info-light">
        <v-tabs v-model="tab">
          <v-tab v-for="item in items" :key="item" :value="item">
            {{ item.name }}
          </v-tab>
        </v-tabs>
        <v-spacer></v-spacer>
      </v-toolbar>
      <v-window v-model="tab" fill-height>
        <v-window-item v-for="item in items" :key="item" :value="item">
          <component :is="item.component"></component>
        </v-window-item>
      </v-window>
    </v-card>

    <!--     <div class="text-center py-3 px-3" v-if="loading">
      <v-progress-circular
        style="text-align: center"
        indeterminate
        color="error"
        size="100"
        width="10"
      ></v-progress-circular>
    </div> -->
  </v-container>
</template>

<script>
import operations from "../service/APIWrapper";
import SpendingModule from "./SpendingModule.vue";

export default {
  name: "DashboardModule",

  data: () => ({
    tab: null,
    items: [
      {
        name: "Spending",
        component: <SpendingModule></SpendingModule>,
      },
      {
        name: "Net Worth",
        component: <SpendingModule></SpendingModule>,
      },
    ],
    chartOptions: {
      title: null,
      legend: {
        enabled: false,
      },
      yAxis: {
        title: null,
        labels: {
          style: {
            color: "#FFFFFF",
            fontSize: "12px",
          },
        },
      },
      series: [
        {
          name: "Price",
          data: [],
          color: "#6661D4",
        },
      ],
      credits: {
        enabled: false,
      },
      chart: {
        backgroundColor: "#18263bb7",
        height: "30%",
        style: {
          fontFamily: "courier",
        },
      },
    },
  }),
  created() {},
  watch: {},
  methods: {
    GetAccounts(filters) {
      operations.GetAccounts(filters).then((response) => {
        this.accounts = response;
      });
    },
  },
};
</script>
