<template>
  <v-card height="70%">
    <v-card-title>Get started</v-card-title>
    <v-row>
      <v-col> <v-btn @click="StartMapping">Map</v-btn> </v-col>
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
            @click="SelectCategory(entry.name)"
          >
            <v-row>
              <v-col cols="6"
                ><v-list-item-header class="py-3 px-3">
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
                </v-list-item-header></v-col
              >
              <v-col cols="6"
                ><v-list-item-header
                  class="py-3 px-3"
                  style="overflow-wrap: break-word"
                >
                  <v-list-item-title
                    style="font-size: 0.8rem"
                    class="font-weight-bold"
                    >{{ entry.category || "" }}
                  </v-list-item-title>
                </v-list-item-header>
              </v-col>
            </v-row>
          </v-list-item>
        </v-list>
      </v-col>
      <v-col>
        <v-autocomplete
          dense
          v-if="anyItemSelected"
          :items="accounts"
          v-model="selectedCategory"
          chips
          outlined
          :readonly="true"
          label="Select Account"
          solo
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
    accounts: [],
    categorize: null,
    selectedItem: null,
    selectedCategory: null,
    accountMatch: null,
    anyItemSelected: false,
  }),
  beforeUpdate() {
    //operations.GetAccounts();
    this.AccountHierarchy();
    console.log("#{test}");
  },
  created() {
    this.GetAccounts("Exclude=Unrealized,Equity,Assets,Pnl,Tax");
    this.StartMapping();
  },
  watch: {
    selectedCategory() {
      if (this.selectedCategory) this.ApplyCategoryToItem();
      else this.anyItemSelected = null;
    },
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
      this.selectedItem = value;
      this.anyItemSelected = true;
    },
    GetAccounts(filters) {
      operations.GetAccounts(filters).then((response) => {
        this.accounts = response;
      });
    },
    ApplyCategoryToItem() {
      //this.categorize.find((entry) => entry.name === this.selectedItem).add("category":this.selectedCategory )
      console.log("found");

      var i = this.categorize.findIndex(
        (entry) => entry.name === this.selectedItem
      );
      console.log();
      this.categorize[i]["category"] = this.selectedCategory;

      var move_entry_to_end = this.categorize.splice(i, 1);
      console.log(move_entry_to_end);

      this.categorize.push(move_entry_to_end.pop());

      this.selectedCategory = null;
      this.selectedItem = null;
    },
  },
};
</script>
