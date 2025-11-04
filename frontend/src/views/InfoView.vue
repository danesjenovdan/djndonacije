<template>
  <div class="checkout">
    <checkout-stage show-terms>
      <!-- <template v-slot:title>{{ $t('infoView.title') }}</template> -->
      <template #title>{{ donationDescriptionForTitle }}</template>
      <template #content>
        <div v-if="loading" class="payment-loader">
          <div class="lds-dual-ring" />
        </div>
        <div class="info-content">
          <p>
            {{ $t("infoView.whyEmail") }}
          </p>
          <div class="form-group">
            <input
              id="email"
              v-model="email"
              type="email"
              :placeholder="$t('infoView.email')"
              class="form-control form-control-lg"
            />
          </div>
          <div v-if="hasNewsletter" class="custom-control custom-checkbox">
            <input
              id="info-newsletter"
              v-model="subscribeToNewsletter"
              type="checkbox"
              name="subscribeNewsletter"
              class="custom-control-input"
            />
            <label class="custom-control-label" for="info-newsletter">{{
              $t("infoView.newsletterLabel")
            }}</label>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="confirm-button-container">
          <confirm-button
            key="next-info"
            :disabled="!canContinueToNextStage"
            :loading="infoSubmitting"
            :text="$t('infoView.next')"
            arrow
            hearts
            @click="continueToNextStage"
          />
        </div>
        <div class="secondary-link">
          <RouterLink :to="{ name: 'selectAmount' }">{{
            $t("infoView.back")
          }}</RouterLink>
        </div>
      </template>
    </checkout-stage>
  </div>
</template>

<script>
import CheckoutStage from "../components/CheckoutStage.vue";
import ConfirmButton from "../components/ConfirmButton.vue";

// https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/email#Validation
const EMAIL_REGEX =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

export default {
  components: {
    ConfirmButton,
    CheckoutStage,
  },
  data() {
    return {
      campaignSlug: this.$route.params.campaignSlug,
      loading: false,
      infoSubmitting: false,
    };
  },
  computed: {
    email: {
      get() {
        return this.$store.getters.getEmail;
      },
      set(value) {
        this.$store.commit("setEmail", value);
      },
    },
    subscribeToNewsletter: {
      get() {
        return this.$store.getters.getSubscribeToNewsletter;
      },
      set(value) {
        this.$store.commit("setSubscribeToNewsletter", value);
      },
    },
    chosenAmount() {
      return this.$store.getters.getChosenAmount;
    },
    recurringDonation() {
      return this.$store.getters.getRecurringDonation;
    },
    hasNewsletter() {
      return this.$store.getters.getHasNewsletter;
    },
    canContinueToNextStage() {
      return this.infoValid && !this.loading;
    },
    infoValid() {
      if (!this.email || !EMAIL_REGEX.test(this.email)) {
        return false;
      }
      // mautic fails after payment if invalid email
      // TODO: fix regex instead of this tmp
      const tmp = this.email.split("@");
      if (tmp.length < 2 || !tmp[1].includes(".")) {
        return false;
      }
      return true;
    },
    lang() {
      return this.$store.getters.getLang;
    },
    donationDescriptionForTitle() {
      if (this.recurringDonation) {
        return this.$t("infoView.monthlyDonationWithAmount", {
          amount: this.chosenAmount,
        });
      }
      return this.$t("infoView.donationWithAmount", {
        amount: this.chosenAmount,
      });
    },
  },
  mounted() {
    if (this.$route.query.znesek) {
      const amount = Number(this.$route.query.znesek);
      this.$store.commit("setChosenAmount", amount);
    }

    if (this.$route.query.mesecna) {
      this.$store.commit("setRecurringDonation", true);
    }

    if (this.chosenAmount <= 0) {
      this.$router.push({ name: "selectAmount" });
    }
  },
  methods: {
    async continueToNextStage() {
      if (this.canContinueToNextStage) {
        this.$router.push({ name: "payment" });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout {
  .info-content {
    width: 100%;
    max-width: 540px;
    margin: 0 auto;

    .alert {
      border-radius: 0;
    }
  }
}
</style>
