<template>
  <v-container>
    <div
      class="fill-height"
      style="width: 100%; height: 100%"
      id="highcharts"
    ></div>
  </v-container>
  <div v-if="refresh"></div>
</template>

<script>
/* eslint-disable */

import Highcharts from "highcharts";
import operations from "../service/APIWrapper";

export default {
  name: "SpendingModule",
  data: () => ({
    refresh: false,
    accounts: null,
    dateRange: null,
    history: [],
    chartOptions: {
      title: null,
      legend: {
        enabled: true,
      },

      series: [],
      credits: {
        enabled: false,
      },
      chart: {
        type: "column",
        backgroundColor: "#18263bb7",
        height: "40%",
        style: {
          fontFamily: "courier",
        },
      },
      plotOptions: {
        series: {
          stacking: "normal",
          events: {
            legendItemClick: function (event) {
              if (!this.visible) {
                this.visible = !this.visible;
              }

              var seriesIndex = this.index;
              var series = this.chart.series;

              for (var i = 0; i < series.length; i++) {
                if (series[i].index != seriesIndex) {
                  series[i].visible = series[i].hide();
                }
              }
              return false;
            },
          },
        },
        /* area: {
          stacking: "percent",
          lineColor: "#ffffff",
          lineWidth: 1,
          marker: {
            lineWidth: 1,
            lineColor: "#ffffff",
          },
        }, */
      },
    },
  }),
  created() {
    this.GetSpending();
  },
  watch: {
    refresh: function () {
      this.InjectToHighcharts();
    },
  },
  methods: {
    GetSpending(filters) {
      var date_range = new Array();
      var accounts = new Array();
      operations
        .GetSpending(["Include=Expenses", "Exclude=Tax", "Year=2021,2022"])
        .then((response) => {
          for (var i in response) {
            var date = new Date(response[i].year, response[i].month, 0);
            var month = date.toLocaleString("default", { month: "long" });
            var y_label = month + " " + response[i].year;

            date_range.push(y_label);
            response[i]["date"] = y_label;

            accounts.push(response[i].account);
          }

          this.dateRange = [...new Set(date_range)];
          this.accounts = [...new Set(accounts)];

          for (var j in this.accounts) {
            this.history.push(
              response.filter((entry) => entry.account === this.accounts[j])
            );
          }
          this.refresh = !this.refresh;
        });
    },
    InjectToHighcharts() {
      var accounts = [];
      var amounts = [];

      //for each account
      this.history.forEach((element, i) => {
        amounts = [];
        element.forEach((subElem) => {
          amounts.push([subElem.date, parseInt(subElem.total.split(" ")[0])]);
          //amounts.push({"date": subElem.date, "value": parseInt(subElem.total.split(" ")[0])});
        });
        accounts.push(amounts);
        this.chartOptions.series.push({
          name: this.history[i][0].account,
          data: accounts[i],
          connectNulls: true,
        });
        this.chartOptions.series[i].name = this.history[i][0].account;
        this.chartOptions.series[i].data = amounts;
      });

      this.chartOptions["xAxis"] = {
        title: "Date",
        categories: this.dateRange,
        labels: {
          format: "{value}",
          style: {
            color: "#FFFFFF",
            fontSize: "12px",
          },
        },
      };
      this.chartOptions["yAxis"] = {
        title: "Amount",
        labels: {
          format: "{text} kr",
          style: {
            color: "#FFFFFF",
            fontSize: "12px",
          },
        },
      };
      this.chartOptions["tooltip"] = {
        headerFormat: "<b>{point.key}</b><br/>",
        pointFormat: "{series.name}: {point.y}<br/>Total: {point.stackTotal}",
      };
      this.chartOptions.title = "Spending";
      Highcharts.chart("highcharts", this.chartOptions);
    },
  },
};
</script>
