<template>
  <div class="checkout">
    <div
      v-if="success && !lastCancelledNewsletter"
      class="alert alert-success text-center"
    >
      <p class="my-3">
        {{ $t("manageNewsletterView.unsubscribeAndDeleteData") }}
      </p>
    </div>
    <div
      v-if="success && lastCancelledNewsletter"
      class="alert alert-success text-center"
    >
      <p class="my-3">
        {{ $t("manageNewsletterView.unsubscribeSuccessful") }}
      </p>
    </div>
    <div v-if="error" class="alert alert-danger text-center">
      <p class="my-3">
        {{ $t("manageNewsletterView.error") }}
      </p>
      <p v-if="errorMessage == 'No such subscriber'" class="my-3">
        <b>{{ $t("manageNewsletterView.noSuchUser") }}</b>
      </p>
      <!-- eslint-disable vue/no-v-html -->
      <p
        class="my-3"
        v-html="
          $t('manageNewsletterView.help', { email: 'vsi@danesjenovdan.si' })
        "
      ></p>
      <!-- eslint-enable vue/no-v-html -->
    </div>

    <checkout-stage no-header show-djnd-footer>
      <template #content>
        <div v-if="showInputForm">
          {{ "TODO: showInputForm" }}
        </div>
        <template v-else>
          <div
            v-for="segment in campaignSubscriptions"
            :key="segment.id"
            class="row justify-content-center my-4"
          >
            <div class="col-md-8">
              <div class="row">
                <div class="col-md-6">
                  <p v-if="segment.id === 21" class="m-0">
                    {{ $t("manageNewsletterView.unsubscribeObcasnik") }}
                  </p>
                  <p v-if="segment.id === 21" class="small-paragraph">
                    {{ $t("manageNewsletterView.unsubscribeObcasnikNote") }}
                  </p>
                  <p v-else class="m-0">
                    {{ $t("manageNewsletterView.unsubscribeNewsletter") }}
                    <strong>{{ segment.name }}</strong
                    >.
                  </p>
                </div>
                <div class="col-md-6">
                  <more-button
                    :disabled="loading"
                    :text="$t('manageNewsletterView.confirmUnsubscribe')"
                    class="my-2"
                    color="secondary"
                    @click="cancelSubscription(segment.name, segment.id)"
                  />
                </div>
              </div>
              <div class="row mt-4">
                <div class="col-12">
                  <hr />
                </div>
              </div>
            </div>
          </div>
          <div class="row justify-content-center mb-4">
            <div class="col-md-4">
              <!-- eslint-disable vue/no-v-html -->
              <p
                class="m-0"
                v-html="$t('manageNewsletterView.unsubscribeFromAll')"
              ></p>
              <!-- eslint-enable vue/no-v-html -->
              <p class="small-paragraph mb-0">
                {{ $t("manageNewsletterView.yourNewsletters") }}:
              </p>
              <ul>
                <li
                  v-for="segment in allSubscriptions"
                  :key="segment.id"
                  class="my-0"
                >
                  {{ segment.name }}
                </li>
              </ul>
              <p class="small-paragraph">
                {{ $t("manageNewsletterView.deleteAllData") }}
              </p>
            </div>
            <div class="col-md-4">
              <more-button
                :disabled="loading"
                :text="$t('manageNewsletterView.confirmDeleteData')"
                class="my-2"
                color="secondary"
                @click="deleteUserData()"
              />
            </div>
          </div>
        </template>
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
    const { campaignSlug } = this.$route.params;

    return {
      campaignSubscriptions: [],
      allSubscriptions: [],
      loading: true,
      campaignSlug,
      email: null,
      token: null,
      success: false,
      error: false,
      errorMessage: "",
      lastCancelledNewsletter: null,
      showInputForm: false, // TODO: true,
    };
  },
  async mounted() {
    const { email, token } = this.$route.query;
    if (!email || !token) {
      this.$router.push("/404");
      // TODO: this.showInputForm = true;
      this.loading = false;
      return;
    }

    this.showInputForm = false;

    // store email and token
    this.$store.commit("setEmail", email);
    this.$store.commit("setToken", token);

    Promise.all([
      this.$store.dispatch("getUserNewsletterSubscriptions", {
        campaign: this.campaignSlug,
      }),
      this.$store.dispatch("getUserNewsletterSubscriptions", {}),
    ])
      .then((responses) => {
        const [campaignResponse, allResponse] = responses;
        if (campaignResponse.status === 200 && allResponse.status === 200) {
          this.campaignSubscriptions = campaignResponse.data.segments;
          this.allSubscriptions = allResponse.data.segments;
        } else {
          this.success = false;
          this.error = true;
          this.showInputForm = true;
        }
      })
      .catch((error) => {
        this.success = false;
        this.error = true;
        this.errorMessage = error?.response?.data?.detail;
        this.showInputForm = true;
      })
      .finally(() => {
        this.loading = false;
      });
  },
  methods: {
    async cancelSubscription(campaignName, segmentId) {
      this.loading = true;

      this.$store
        .dispatch("cancelNewsletterSubscription", {
          segment_id: segmentId,
        })
        .then((response) => {
          if (response.status === 200) {
            this.campaignSubscriptions = this.campaignSubscriptions.filter(
              (campaign) => campaign.id !== segmentId,
            );
            this.allSubscriptions = this.allSubscriptions.filter(
              (campaign) => campaign.id !== segmentId,
            );
            this.success = true;
            this.lastCancelledNewsletter = campaignName;
          } else {
            this.success = false;
            this.error = true;
          }
        })
        .catch((error) => {
          this.success = false;
          this.error = true;
          this.errorMessage = error?.response?.data?.detail;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    async deleteUserData() {
      this.loading = true;

      this.$store
        .dispatch("deleteUserData")
        .then((response) => {
          if (response.status === 204) {
            this.campaignSubscriptions = [];
            this.allSubscriptions = [];
            this.success = true;
            this.lastCancelledNewsletter = null;
          } else {
            this.success = false;
            this.error = true;
          }
        })
        .catch((error) => {
          this.success = false;
          this.error = true;
          this.errorMessage = error?.response?.data?.detail;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";
@import "~bootstrap/scss/mixins/breakpoints";

.checkout-stage {
  p,
  li {
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

  p.small-paragraph,
  li {
    font-size: 16px;
  }
}
</style>
