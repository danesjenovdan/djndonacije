<template>
  <div class="checkout">
    <div v-if="success" class="alert alert-success text-center">
      <p class="my-3">
        Mesečna donacija za {{ last_cancelled_campaign }} je uspešno prekinjena.
      </p>
    </div>
    <div v-if="error" class="alert alert-danger text-center">
      <p class="my-3">
        Zgodila se je napaka. Tvoja mesečna donacija je še vedno aktivna.
        <br />Piši nam na
        <a href="mailto:vsi@danesjenovdan.si">vsi@danesjenovdan.si</a> in bomo
        takoj razrešili težavo.
      </p>
    </div>
    <checkout-stage no-header show-djnd-footer>
      <template v-slot:content>
        <div
          class="row justify-content-center my-4"
          v-for="donationCampaign in this.campaign_subscriptions"
          :key="donationCampaign.id"
        >
          <div class="col-md-4">
            <p class="m-0">
              Odjavi me od donacij:
              <strong>{{ donationCampaign.campaign.name }}</strong>
            </p>
          </div>
          <div class="col-md-4">
            <more-button
              :disabled="loading"
              :text="'Da, potrjujem preklic.'"
              class="my-2"
              color="secondary"
              @click="
                cancelDonation(
                  donationCampaign.campaign.name,
                  donationCampaign.subscription_id
                )
              "
            />
          </div>
        </div>
        <div
          v-if="this.campaign_subscriptions.length === 0"
          class="row justify-content-center my-4"
        >
          <div class="col-md-8">
            <p class="m-0 text-center">
              Trenutno nimaš aktivne nobene mesečne donacije.
            </p>
          </div>
        </div>
        <div v-if="loading" class="payment-loader">
          <div class="lds-dual-ring" />
        </div>
      </template>
    </checkout-stage>
  </div>
</template>

<script>
import CheckoutStage from "../components/CheckoutStage.vue";
import MoreButton from "../components/MoreButton.vue";

export default {
  components: {
    CheckoutStage,
    MoreButton,
  },
  data() {
    return {
      campaign_subscriptions: [],
      loading: true,
      last_cancelled_campaign: null,
      success: false,
      error: false,
      error_message: "",
    };
  },
  async mounted() {
    // store token
    const token = this.$route.query.token;
    if (token) {
      this.$store.commit("setToken", token);
    }
    // store email
    const email = this.$route.query.email;
    if (email) {
      this.$store.commit("setEmail", email);
    }

    if (!(email && token)) {
      this.$router.push("/404");
    }

    // get subscriptions list
    this.$store
      .dispatch("getUserDonations")
      .then((response) => {
        if (response.status === 200) {
          this.campaign_subscriptions = response.data;
        } else {
          // catch error
          console.log("Not successful", response);
          this.success = false;
          this.error = true;
        }
      })
      .catch((error) => {
        // catch error
        console.log("Error", error);
        this.success = false;
        this.error = true;
      })
      .finally(() => {
        this.loading = false;
      });
  },
  methods: {
    async cancelDonation(campaign_name, subscription_id) {
      this.loading = true;

      this.$store
        .dispatch("cancelDonationSubscription", {
          subscription_id: subscription_id,
        })
        .then((response) => {
          if (response.status === 200) {
            this.campaign_subscriptions = this.campaign_subscriptions.filter(
              (campaign) => campaign.subscription_id != subscription_id
            );
            this.success = true;
            this.last_cancelled_campaign = campaign_name;
          } else {
            // catch error
            console.log("Not successful", response);
            this.success = false;
            this.error = true;
          }
        })
        .catch((error) => {
          // catch error
          this.success = false;
          this.error = true;
          console.log("Error", error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout-stage {
  p {
    font-size: 20px;
    color: #333333;
    font-weight: 200;
    width: 100%;
    max-width: 872px;
    margin-top: 20px;
    margin-bottom: 20px;
    padding-left: 30px;
    padding-right: 30px;

    @include media-breakpoint-up(md) {
      font-size: 30px;
      padding: 0;
    }
  }
}
</style>
