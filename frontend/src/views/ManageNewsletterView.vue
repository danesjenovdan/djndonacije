<template>
  <div class="checkout">
    <div v-if="success && !last_cancelled_newsletter" class="alert alert-success text-center">
      <p class="my-3">
        {{ $t('manageNewsletterView.unsubscribeAndDeleteData') }}
      </p>
    </div>
    <div v-if="success && last_cancelled_newsletter" class="alert alert-success text-center">
      <p class="my-3">
        {{ $t('manageNewsletterView.unsubscribeSuccessful') }}
      </p>
    </div>
    <div v-if="error" class="alert alert-danger text-center">
      <p class="my-3">
        {{ $t('manageNewsletterView.error') }}
      </p>
      <p v-if="errorMessage == 'No such subscriber'" class="my-3">
        <b>{{ $t('manageNewsletterView.noSuchUser') }}</b>
      </p>
      <p class="my-3" v-html="$t('manageNewsletterView.help', { email: 'vsi@danesjenovdan.si'})"></p>
    </div>

    <checkout-stage no-header :show-djnd-footer="true">
      <template v-slot:content>
        <div class="row justify-content-center my-4" v-for="segment in this.campaignSubscriptions" :key="segment.id">
          <div class="col-md-8">
            <div class="row">
              <div class="col-md-6">
                <p class="m-0" v-if="segment.id === 21">
                  {{ $t('manageNewsletterView.unsubscribeObcasnik') }}
                </p>
                <p class="small-paragraph" v-if="segment.id === 21">
                  {{ $t('manageNewsletterView.unsubscribeObcasnikNote') }}
                </p>
                <p class="m-0" v-else>
                  {{ $t('manageNewsletterView.unsubscribeNewsletter') }} <strong>{{ segment.name }}</strong>.
                </p>
              </div>
              <div class="col-md-6">
                <more-button :disabled="loading"
                  :text="$t('manageNewsletterView.confirmUnsubscribe')"
                  class="my-2" color="secondary" @click="cancelSubscription(segment.name, segment.id)" />
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
            <p class="m-0" v-html="$t('manageNewsletterView.unsubscribeFromAll')"></p>
            <p class="small-paragraph mb-0">{{ $t('manageNewsletterView.yourNewsletters') }}:</p>
            <ul>
              <li v-for="segment in this.allSubscriptions" class="my-0">{{ segment.name }}</li>
            </ul>
            <p class="small-paragraph">
              {{ $t('manageNewsletterView.deleteAllData') }}
            </p>
          </div>
          <div class="col-md-4">
            <more-button :disabled="loading"
              :text="$t('manageNewsletterView.confirmDeleteData')" class="my-2"
              color="secondary" @click="deleteUserData()" />
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
  props: ["lang"],
  components: {
    CheckoutStage,
    MoreButton,
  },
  data() {
    const campaignSlug = this.$route.params.campaignSlug;

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
      last_cancelled_newsletter: null,
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

    // get campaign subscriptions list
    this.$store
      .dispatch("getUserNewsletterSubscriptions", {
        campaign: this.campaignSlug,
      })
      .then((response) => {
        if (response.status === 200) {
          this.campaignSubscriptions = response.data.segments;
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
        this.errorMessage = error?.response?.data?.detail
      })
      .finally(() => {
        this.loading = false;
      });

    // get all subscriptions list
    this.$store
      .dispatch("getUserNewsletterSubscriptions", {})
      .then((response) => {
        if (response.status === 200) {
          this.allSubscriptions = response.data.segments;
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
        this.errorMessage = error?.response?.data?.detail
      })
      .finally(() => {
        this.loading = false;
      });
  },
  methods: {
    async cancelSubscription(campaign_name, segment_id) {
      this.loading = true;

      this.$store
        .dispatch("cancelNewsletterSubscription", {
          segment_id: segment_id,
        })
        .then((response) => {
          if (response.status === 200) {
            this.campaignSubscriptions = this.campaignSubscriptions.filter(
              (campaign) => campaign.id != segment_id
            );
            this.allSubscriptions = this.allSubscriptions.filter(
              (campaign) => campaign.id != segment_id
            );
            this.success = true;
            this.last_cancelled_newsletter = campaign_name;
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
          this.errorMessage = error?.response?.data?.detail
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
            this.subscriptions = [];
            this.success = true;
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
          this.errorMessage = error?.response?.data?.detail
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
  p, li {
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

  p.small-paragraph, li {
    font-size: 16px;
  }
}</style>
