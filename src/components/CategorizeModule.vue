<template>
  <v-card height="70%">
    <v-card-title>Get started</v-card-title>
    <v-row>
      <v-col> <v-btn @click="StartMapping">Map</v-btn> </v-col>
      <v-col>
        <v-btn @click="AccountHierarchy">Let's Categorize </v-btn>
      </v-col>
    </v-row>
    <v-row class="overflow-y-auto">
      <v-col cols="4">
        <v-list dense>
          <v-list-item
            v-for="entry in categorize"
            :key="entry.name"
            lines="3"
            variant="outlined"
            class="py-0 px-3 mx-5 my-1"
            rounded="xl"
            active-color="primary"
            @click="SelectCategory(entry)"
          >
            <v-list-item-header class="py-3 px-3">
              <v-list-item-title
                style="font-size: 0.8rem"
                class="font-weight-bold"
                >{{ entry.name }}
              </v-list-item-title>
              <v-list-item-subtitle style="font-size: 0.8rem">
                on {{ entry.date }}
              </v-list-item-subtitle>
              <v-list-item-subtitle style="font-size: 0.7rem">
                for {{ entry.amount }} {{ entry.currency }}
              </v-list-item-subtitle>
            </v-list-item-header>
          </v-list-item>
        </v-list>
      </v-col>
      <v-col>
        <v-autocomplete
          dense
          v-if="itemSelected"
          :items="accounts.account"
          chips
        ></v-autocomplete
      ></v-col>
    </v-row>
    <v-autocomplete
      dense
      v-if="accountMatch"
      :items="accountMatch"
      chips
    ></v-autocomplete>
  </v-card>
</template>

<script>
import operations from "../service/APIWrapper";

export default {
  name: "CategorizeModule",

  data: () => ({
    accounts: [
      {
        account: "Assets:Investment:Nordnet:Depot:Cash",
      },
      {
        account: "Equity:Opening-Balance",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:AGILC",
      },
      {
        account: "Assets:DanskeBank:Checking",
      },
      {
        account: "Expenses:Consumption:EatingOut",
      },
      {
        account: "Expenses:Subscription:Insurance",
      },
      {
        account: "Expenses:Housing:Rent",
      },
      {
        account: "Expenses:Subscription:Mobile",
      },
      {
        account: "Expenses:Consumption:Grocery",
      },
      {
        account: "Expenses:Subscription:Other",
      },
      {
        account: "Income:Work:NetSalary",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPVBEUKL",
      },
      {
        account: "Expenses:Trading:Commissions",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPVBUSAKL",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPIDJWKL",
      },
      {
        account: "Expenses:Tax",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPIUSVKL",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPVIBGKL",
      },
      {
        account: "Expenses:Housing:Utilities",
      },
      {
        account: "Expenses:Consumption:Vacation",
      },
      {
        account: "Income:Investment:Nordnet:PnL:Dividends",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:GMAB",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:TRYG",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:VWS",
      },
      {
        account: "Expenses:Consumption:Activities",
      },
      {
        account: "Expenses:Consumption:Health",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:ORSTED",
      },
      {
        account: "Expenses:Housing:Maintenance",
      },
      {
        account: "Income:Work:Bonus",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:Cash",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:SPIDJWKL",
      },
      {
        account: "Expenses:Consumption:Transport",
      },
      {
        account: "Expenses:Housing:Household",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:SPIC25KL",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:SPIUSGKL",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:SPVBUSAKL",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:XACTC25",
      },
      {
        account: "Expenses:Consumption:Other",
      },
      {
        account: "Expenses:Consumption:Gifts",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:IQQH",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPIC25KL",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:EUNL",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:IQQH",
      },
      {
        account: "Income:Investment:SaxoBank:PnL:Sales",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:XDWM",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:XDWM",
      },
      {
        account: "Expenses:Consumption:Clothes",
      },
      {
        account: "Income:Investment:Nordnet:PnL:Sales",
      },
      {
        account: "Assets:Investment:SaxoBank:Depot:Cash",
      },
      {
        account: "Expenses:Consumption:Tech",
      },
      {
        account: "Expenses:Consumption:Office",
      },
      {
        account: "Income:Investment:SaxoBank:PnL:Dividends",
      },
      {
        account: "Income:Work:GrossSalary",
      },
      {
        account: "Income:Pension:Firmabidrag",
      },
      {
        account: "Assets:Investment:Pension:Firmabidrag",
      },
      {
        account: "Assets:Investment:Pension:Egenbidrag",
      },
      {
        account: "Expenses:Tax:ATP",
      },
      {
        account: "Expenses:Tax:AM-bidrag",
      },
      {
        account: "Expenses:Tax:A-skat",
      },
      {
        account: "Expenses:Consumption:Lunch",
      },
      {
        account: "Assets:Investment:SaxoBank:Depot:SPIC25KL",
      },
      {
        account: "Assets:Investment:SaxoBank:Depot:GMAB",
      },
      {
        account: "Assets:Investment:SaxoBank:Depot:LINKFI",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:AGILC:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:AGILC:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:EUNL:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:EUNL:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:GMAB:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:GMAB:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:IQQH:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:IQQH:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:ORSTED:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:ORSTED:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPIC25KL:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:SPIC25KL:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPIDJWKL:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:SPIDJWKL:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:SPVIBGKL:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:SPVIBGKL:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:TRYG:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:TRYG:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:VWS:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:VWS:Unrealized",
      },
      {
        account: "Assets:Investment:Nordnet:Depot:XDWM:Unrealized",
      },
      {
        account: "Income:Investment:Nordnet:Depot:XDWM:Unrealized",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:IQQH:Unrealized",
      },
      {
        account: "Income:Investment:SaxoBank:ASK:IQQH:Unrealized",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:XACTC25:Unrealized",
      },
      {
        account: "Income:Investment:SaxoBank:ASK:XACTC25:Unrealized",
      },
      {
        account: "Assets:Investment:SaxoBank:ASK:XDWM:Unrealized",
      },
      {
        account: "Income:Investment:SaxoBank:ASK:XDWM:Unrealized",
      },
      {
        account: "Assets:Investment:SaxoBank:Depot:GMAB:Unrealized",
      },
      {
        account: "Income:Investment:SaxoBank:Depot:GMAB:Unrealized",
      },
      {
        account: "Assets:Investment:SaxoBank:Depot:LINKFI:Unrealized",
      },
      {
        account: "Income:Investment:SaxoBank:Depot:LINKFI:Unrealized",
      },
      {
        account: "Assets:Investment:SaxoBank:Depot:SPIC25KL:Unrealized",
      },
      {
        account: "Income:Investment:SaxoBank:Depot:SPIC25KL:Unrealized",
      },
    ],
    categorize: null,
    accountMatch: null,
    itemSelected: false,
  }),
  beforeUpdate() {
    //operations.GetAccounts();
    this.AccountHierarchy();
    console.log("#{test}");
  },
  methods: {
    StartMapping() {
      operations.RunCategorize().then((response) => {
        this.categorize = response.values;
      });
    },
    AccountHierarchy() {
      var account_set = [new Set(), new Set(), new Set()];
      for (var i in this.accounts) {
        account_set[0].add(this.accounts[i].account.split(":")[0]);
        account_set[1].add(this.accounts[i].account.split(":")[1]);
        account_set[2].add(this.accounts[i].account.split(":")[2]);
      }
      this.accountMatch = Array.from(account_set[0]);
      console.log(account_set);
    },
    SelectCategory(value) {
      console.log(value);
      this.itemSelected = !this.itemSelected;
    },
  },
};
</script>
