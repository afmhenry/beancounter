<template>
  <v-container>
    <div style="text-align: center">
      <h1>Categorize these transactions</h1>
      <br />
    </div>
    <div
      class="text-center py-3 px-3"
      v-if="
        categorize.length === 0 &&
        categorized.length === 0 &&
        !nothingToCategorize
      "
    >
      <v-progress-circular
        style="text-align: center"
        indeterminate
        color="primary"
        size="100"
        width="10"
      ></v-progress-circular>
    </div>
    <v-row v-else-if="nothingToCategorize">
      <div style="text-align: center">
        <h3>Nothing left to categorize. Lets import!</h3>
        <br />
      </div>
    </v-row>
    <v-row v-else>
      <v-col cols="4" max-height="100%" style="color: primary">
        <v-card>
          <v-card-title>Select</v-card-title>
          <v-card-subtitle>
            These purchases aren't mapped to a category.
          </v-card-subtitle>

          <br />
          <v-list dense allow-overflow>
            <v-list-item
              v-for="(entry, index) in categorize"
              :key="entry.name"
              lines="3"
              variant="outlined"
              class="py-0 px-3 mx-5 my-1"
              rounded="xl"
              :class="{
                'v-list-item--active text-primary': index === selectedItem,
              }"
              @click="SelectCategory(index)"
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
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card>
          <v-card-title>Assign</v-card-title>
          <v-card-subtitle
            >Assign the transaction to an account, so it is properly
            categorized.
          </v-card-subtitle>
          <br />
          <v-autocomplete
            dense
            :items="accounts"
            v-model="selectedCategory"
            chips
            outlined
            class="px-5"
            :disabled="!anyItemSelected"
            :readonly="true"
            label="Select Account"
            solo
          ></v-autocomplete
        ></v-card>
        <v-card>
          <v-card-title>Update</v-card-title>
          <v-card-subtitle
            >Update your mapping, so these transactions can be imported.
          </v-card-subtitle>
          <br />
          <div style="text-align: center" class="py-5">
            <v-btn
              color="secondary"
              :disabled="categorize.length !== 0"
              @click="SubmitCategories"
              >Submit Updates</v-btn
            >
          </div>
        </v-card></v-col
      >
      <v-col cols="4">
        <v-card>
          <v-card-title>Newly categorized</v-card-title>
          <v-card-subtitle>
            These purchases are categorized, but make sure to submit before
            leaving the page.
          </v-card-subtitle>
          <v-list dense>
            <v-list-item
              v-for="(entry, index) in categorized"
              :key="entry.name"
              lines="3"
              variant="outlined"
              class="py-0 px-3 mx-5 my-1"
              rounded="xl"
              :class="{
                'v-list-item--active text-warning-light': index === 0,
              }"
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
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import operations from "../service/APIWrapper";

export default {
  name: "CategorizeModule",

  data: () => ({
    accounts: [],
    categorize: [],
    categorized: [],
    nothingToCategorize: false,
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
      operations.InvokeScript("map").then((response) => {
        if (response.values.length === 0) {
          this.nothingToCategorize = true;
        }
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
    SelectCategory(index) {
      this.selectedItem = index;
      this.anyItemSelected = true;
    },
    GetAccounts(filters) {
      operations.GetAccounts(filters).then((response) => {
        this.accounts = response;
      });
    },
    ApplyCategoryToItem() {
      //this.categorize.find((entry) => entry.name === this.selectedItem).add("category":this.selectedCategory )
      this.categorize[this.selectedItem]["category"] = this.selectedCategory;
      var move_entry_to_end = this.categorize.splice(this.selectedItem, 1);
      this.categorized.unshift(move_entry_to_end.pop());

      //reset for next-probably have more work to do.
      this.selectedCategory = null;
      this.selectedItem = null;
    },
    SubmitCategories() {
      operations.SendUpdatedCategories(this.categorized).then(() => {
        window.location.reload();
      });
    },
  },
};
</script>
