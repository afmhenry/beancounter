<template>
  <v-container>
    <h1>Hi</h1>
    <div
      class="fill-height"
      style="width: 100%; height: 100%"
      id="highcharts"
    ></div>
  </v-container>
  <div v-if="refresh"></div>
</template>

<script>
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
        enabled: false,
      },
      yAxis: {
        title: null,
        labels: {
          format: "{date}",
          style: {
            color: "#FFFFFF",
            fontSize: "12px",
          },
        },
      },
      series: [],
      credits: {
        enabled: false,
      },
      chart: {
        type: "bar",
        backgroundColor: "#18263bb7",
        height: "40%",
        style: {
          fontFamily: "courier",
        },
      },
      plotOptions: {
        series: {
          stacking: "normal",
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
        .GetSpending([
          "Include=Expenses",
          "Exclude=Tax,Housing",
          "Year=2022",
          "Month=1,2,3,4",
        ])
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
        labels: {
          format: "{date}",
          style: {
            color: "#FFFFFF",
            fontSize: "12px",
          },
        },
      };

      this.chartOptions["tooltip"] = {
        headerFormat: "<b>{point.x}</b><br/>",
        pointFormat: "{series.name}: {point.y}<br/>Total: {point.stackTotal}",
      };
      this.chartOptions.title = "Spending";
      Highcharts.chart("highcharts", this.chartOptions);
    },
  },
};
</script>
