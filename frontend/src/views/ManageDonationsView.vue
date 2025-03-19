<template>
  <div class="checkout">
    <div v-if="success" class="alert alert-success text-center">
      <p class="my-3">
        {{
          $t("manageDonationsView.cancelDonation", {
            don: last_cancelled_campaign,
          })
        }}
      </p>
    </div>
    <div v-if="error" class="alert alert-danger text-center">
      <!-- eslint-disable vue/no-v-html -->
      <p
        class="my-3"
        v-html="$t('manageDonationsView.cancelDonationError')"
      ></p>
      <!-- eslint-enable vue/no-v-html -->
    </div>
    <checkout-stage no-header show-djnd-footer>
      <template #content>
        <div
          v-for="donationCampaign in campaign_subscriptions"
          :key="donationCampaign.id"
          class="row justify-content-center my-4"
        >
          <div class="col-md-4">
            <p class="m-0">
              {{ $t("manageDonationsView.cancelMyDonation") }}
              <strong>{{ donationCampaign.campaign.name }}</strong>
            </p>
          </div>
          <div class="col-md-4">
            <more-button
              :disabled="loading"
              :text="$t('manageDonationsView.confirmCancellation')"
              class="my-2"
              color="secondary"
              @click="
                cancelDonation(
                  donationCampaign.campaign.name,
                  donationCampaign.subscription_id,
                )
              "
            />
          </div>
        </div>
        <div
          v-if="campaign_subscriptions.length === 0"
          class="row justify-content-center my-4"
        >
          <div class="col-md-8">
            <p class="m-0 text-center">
              {{ $t("manageDonationsView.noActiveDonation") }}
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
    const { token } = this.$route.query;
    if (token) {
      this.$store.commit("setToken", token);
    }
    // store email
    const { email } = this.$route.query;
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
          // eslint-disable-next-line no-console
          console.log("Not successful", response);
          this.success = false;
          this.error = true;
        }
      })
      .catch((error) => {
        // catch error
        // eslint-disable-next-line no-console
        console.log("Error", error);
        this.success = false;
        this.error = true;
      })
      .finally(() => {
        this.loading = false;
      });
  },
  methods: {
    async cancelDonation(campaignName, subscriptionId) {
      this.loading = true;

      this.$store
        .dispatch("cancelDonationSubscription", {
          subscription_id: subscriptionId,
        })
        .then((response) => {
          if (response.status === 200) {
            this.campaign_subscriptions = this.campaign_subscriptions.filter(
              (campaign) => campaign.subscription_id != subscriptionId,
            );
            this.success = true;
            this.last_cancelled_campaign = campaignName;
          } else {
            // catch error
            // eslint-disable-next-line no-console
            console.log("Not successful", response);
            this.success = false;
            this.error = true;
          }
        })
        .catch((error) => {
          // catch error
          this.success = false;
          this.error = true;
          // eslint-disable-next-line no-console
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
