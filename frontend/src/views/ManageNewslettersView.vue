<template>
  <div class="checkout">
    <div v-if="success" class="alert alert-success text-center">
      <p class="my-3">
        {{ $t("manageNewsletterView.unsubscribeSuccessful") }}
      </p>
    </div>
    <div v-if="error" class="fixed-top alert alert-danger text-center">
      <!-- eslint-disable vue/no-v-html -->
      <p
        class="my-3"
        v-html="$t('manageNewsletterView.cancelSubscriptionError')"
      ></p>
      <!-- eslint-enable vue/no-v-html -->
    </div>
    <checkout-stage no-header show-djnd-footer>
      <template #content v-if="showInputForm">
        <div class="row">
          <div class="col-md-10 offset-md-1">
            <h1 class="text-center">
              {{ $t("manageNewsletterView.unsubscribeNewsletters") }}
            </h1>
          </div>
        </div>
        <div class="row my-4 email-form">
          <div class="col-md-6 offset-md-3">
            <p class="m-0 text-center">
              {{ $t("manageNewsletterView.enterEmail") }}
            </p>
            <div class="form-group">
              <input
                v-model="linkEmail"
                type="email"
                class="form-control my-3"
                :placeholder="$t('infoView.email')"
                :disabled="loading || linkSent"
              />
            </div>
            <div class="form-group">
              <div class="captcha-container">
                <div v-if="robotError" class="alert alert-danger py-2 my-2">
                  {{ $t("infoView.wrongAnswer") }}
                </div>
                <div ref="captcha"></div>
              </div>
              <p v-if="!linkSent" class="bots-text">
                {{ $t("infoView.bots") }}
              </p>
            </div>
            <div v-if="linkSent" class="link-sent-message">
              <p class="my-3">
                {{ $t("manageDonationsView.emailSent") }}
              </p>
            </div>
            <div v-if="!linkSent" class="form-group text-center">
              <more-button
                :disabled="loading || invalidEmail(linkEmail) || linkSent"
                :text="$t('manageDonationsView.sendLink')"
                color="primary"
                @click="sendCancellationLink"
              />
            </div>
          </div>
        </div>
        <div v-if="loading" class="payment-loader">
          <div class="lds-dual-ring" />
        </div>
      </template>
      <template #content v-else>
        <div class="row">
          <div class="col-md-10 offset-md-1">
            <h1>{{ $t("manageNewsletterView.unsubscribeNewsletters") }}</h1>
          </div>
        </div>
        <div
          v-for="newsletter in campaign_subscriptions"
          :key="newsletter.id"
          class="row my-4"
        >
          <div class="col-md-5 offset-md-1">
            <div class="donation-name">
              {{ newsletter.name }}
            </div>
            <div class="donation-created-date">
              {{
                $t("manageDonationsView.donationCreatedOn", {
                  date: formatDate(newsletter.dateAdded),
                })
              }}
            </div>
          </div>
          <div class="col-md-5">
            <more-button
              :disabled="loading"
              :text="$t('manageNewsletterView.confirmUnsubscribe')"
              class="my-2"
              color="secondary"
              @click="cancelSubscription(newsletter.name, newsletter.id)"
            />
          </div>
        </div>
        <div
          v-if="campaign_subscriptions.length === 0"
          class="row justify-content-center my-4"
        >
          <div class="col-md-8">
            <p class="m-0 text-center">
              {{ $t("manageNewsletterView.noActiveSubscription") }}
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
      showInputForm: false,
      linkEmail: "",
      linkSent: false,
      campaign_subscriptions: [],
      loading: true,
      last_cancelled_campaign: null,
      success: false,
      error: false,
      error_message: "",
      robotError: false,
    };
  },
  async mounted() {
    const { email, token } = this.$route.query;
    if (!email || !token) {
      this.showInputForm = true;
      this.loading = false;
      this.$nextTick(() => {
        this.loadCaptcha();
      });
      return;
    }

    // store email and token
    this.$store.commit("setEmail", email);
    this.$store.commit("setToken", token);

    // get subscriptions list
    this.$store
      .dispatch("getUserNewsletterSubscriptions", {})
      .then((response) => {
        if (response.status === 200) {
          this.campaign_subscriptions = response.data.segments;
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
    async cancelSubscription(campaignName, subscriptionId) {
      this.loading = true;

      this.$store
        .dispatch("cancelNewsletterSubscription", {
          segment_id: subscriptionId,
        })
        .then((response) => {
          if (response.status === 200) {
            this.campaign_subscriptions = this.campaign_subscriptions.filter(
              (campaign) => campaign.id != subscriptionId,
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
    loadCaptcha() {
      if (this.$refs.captcha && !document.querySelector("#vajbcha")) {
        const s = document.createElement("script");
        s.dataset.inputName = "captcha";
        s.dataset.locale = this.lang;
        s.src = "https://vajbcha.danesjenovdan.si/js/vajbcha.js";
        this.$refs.captcha.appendChild(s);
      }
    },
    formatDate(dateString) {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(dateString).toLocaleDateString("sl-SI", options);
    },
    formatType(type) {
      if (type.includes("braintree")) {
        return this.$t("payment.card");
      }
      if (type.includes("flik")) {
        return this.$t("payment.flik");
      }
      return type;
    },
    invalidEmail(email) {
      if (!email) return true;
      if (!email.includes("@")) return true;
      return false;
    },
    sendCancellationLink() {
      this.loading = true;
      this.robotError = false;

      const captchaApi = window.vajbcha.captcha;
      if (!captchaApi) {
        this.loading = false;
        this.robotError = true;
        return;
      }

      this.$store
        .dispatch("sendNewslettersEditLink", {
          email: this.linkEmail,
          captcha: captchaApi.value(),
        })
        .then((response) => {
          captchaApi.remove();
          this.loading = false;
          this.robotError = false;
          this.linkSent = true;
        })
        .catch((error) => {
          const code = error.status || 500;
          const msg =
            error?.response?.data?.status || error?.response?.data?.msg || "";
          if (code === 403 && msg.toLowerCase().includes("captcha")) {
            captchaApi.reload();
            this.loading = false;
            this.robotError = true;
            this.linkSent = false;
          } else if (code === 400 && msg.toLowerCase().includes("email")) {
            // eslint-disable-next-line no-console
            console.log("Error", error);
            // invalid email (just pretend it was successful)
            captchaApi.remove();
            this.loading = false;
            this.robotError = false;
            this.linkSent = true;
          } else {
            // catch error
            this.success = false;
            this.error = true;
            // eslint-disable-next-line no-console
            console.log("Error", error);
          }
        });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout-stage {
  h1 {
    font-size: 2rem;
  }

  .donation-name {
    font-size: 1.5rem;
    font-weight: 500;
  }

  .donation-amount,
  .donation-created-date {
    font-size: 1rem;
    font-weight: 300;
  }

  .email-form {
    p {
      font-size: 1.2rem;
      font-weight: 300;
    }

    input {
      max-width: 350px;
      margin-inline: auto;
      font-size: 1.2rem;

      &:disabled {
        background-color: #e9ecef;
        cursor: default;
      }
    }

    .bots-text {
      max-width: 360px;
      margin: 0 auto;
      padding-top: 1rem;
      font-size: 1rem;
      font-weight: 300;
      text-align: center;
    }

    .captcha-container {
      .alert {
        max-width: 360px;
        margin-inline: auto;
      }

      :deep(#vajbcha) {
        iframe {
          margin-inline: auto;
        }
      }
    }

    .link-sent-message {
      p {
        font-size: 1.2rem;
        font-weight: 500;
        text-align: center;
      }
    }
  }
}
</style>
