<template>
  <div class="checkout">
    <div v-if="error" class="alert alert-danger">
      <p>
        {{ $t("paymentView.errorMessage") }}
        <strong>{{
          error.error && error.error.message ? error.error.message : error.data
        }}</strong>
      </p>
      <p>
        {{ $t("paymentView.errorHelp1") }}
        <a href="mailto:vsi@danesjenovdan.si">vsi@danesjenovdan.si</a>
        {{ $t("paymentView.errorHelp2") }}
      </p>
    </div>
    <checkout-stage show-terms>
      <template #title>{{ $t("paymentView.title") }}</template>
      <template #content>
        <div class="payment-container">
          <payment-switcher
            :recurring="recurringDonation"
            :has-upn="paymentOptions.upn"
            :has-flik="paymentOptions.flik"
            @change="onPaymentChange"
          />
          <div v-if="checkoutLoading" class="payment-loader">
            <div class="lds-dual-ring" />
          </div>
          <template v-if="payment === 'card'">
            <card-payment
              :token="token"
              :amount="chosenAmount"
              :email="email"
              @ready="onPaymentReady"
              @validity-change="paymentInfoValid = $event"
              @payment-start="paymentInProgress = true"
              @success="paymentSuccess"
              @error="paymentError"
            />
          </template>
          <template v-if="payment === 'upn'">
            <upn-payment
              :amount="chosenAmount"
              @ready="onUPNPaymentReady"
              @success="paymentSuccess"
            />
          </template>
          <template v-if="payment === 'flik'">
            <flik-payment
              :amount="chosenAmount"
              @ready="onFlikPaymentReady"
              @success="paymentSuccess"
            />
          </template>
          <div class="cart-total">
            <span>{{ $t("paymentView.amountToPay") }}</span>
            <i>{{ chosenAmount }} €</i>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="confirm-button-container">
          <confirm-button
            key="next-payment"
            :disabled="!canContinueToNextStage"
            :loading="paymentInProgress"
            :text="$t('paymentView.donate')"
            arrow
            hearts
            @click="continueToNextStage"
          />
        </div>
        <div class="secondary-link">
          <RouterLink :to="{ name: 'info', params: $route.params }">{{
            $t("paymentView.back")
          }}</RouterLink>
        </div>
      </template>
    </checkout-stage>
  </div>
</template>

<script>
import CheckoutStage from "../components/CheckoutStage.vue";
import ConfirmButton from "../components/ConfirmButton.vue";
import CardPayment from "../components/Payment/Card.vue";
import UpnPayment from "../components/Payment/Upn.vue";
import FlikPayment from "../components/Payment/Flik.vue";
import PaymentSwitcher from "../components/Payment/Switcher.vue";

export default {
  components: {
    ConfirmButton,
    CheckoutStage,
    CardPayment,
    UpnPayment,
    FlikPayment,
    PaymentSwitcher,
  },
  data() {
    const { campaignSlug } = this.$route.params;
    const payment =
      this.$store.getters.getPaymentOptions.oneTime ||
      this.$store.getters.getPaymentOptions.monthly
        ? "card"
        : "upn";
    const { lang } = this.$route.params;

    return {
      campaignSlug,
      lang,
      error: null,
      payment,
      checkoutLoading: false,
      paymentInfoValid: false,
      paymentInProgress: false,
      payFunction: undefined,
    };
  },
  computed: {
    token() {
      return this.$store.getters.getToken;
    },
    customerId() {
      return this.$store.getters.getCustomerId;
    },
    email() {
      return this.$store.getters.getEmail;
    },
    recurringDonation() {
      return this.$store.getters.getRecurringDonation;
    },
    paymentOptions() {
      return this.$store.getters.getPaymentOptions;
    },
    chosenAmount() {
      return this.$store.getters.getChosenAmount;
    },
    thankYouUrl() {
      return this.$store.getters.getRedirectToThankYou;
    },
    canContinueToNextStage() {
      return this.payFunction && this.paymentInfoValid;
    },
  },
  mounted() {
    if (this.$route.query.znesek) {
      const amount = Number(this.$route.query.znesek);
      this.$store.commit("setChosenAmount", amount);
    }

    // redirect if no amount
    if (this.chosenAmount <= 0) {
      this.$router.push({ name: "selectAmount" });
    }

    // redirect if no token or customerid or email
    if (this.token === "" || this.customerId === "" || this.email === "") {
      this.$router.push({ name: "info" });
    }
  },
  methods: {
    onPaymentReady({ pay } = {}) {
      this.checkoutLoading = false;
      this.paymentInfoValid = false;
      this.payFunction = pay;
    },
    onUPNPaymentReady({ pay } = {}) {
      this.checkoutLoading = false;
      this.paymentInfoValid = true;
      this.payFunction = pay;
    },
    onFlikPaymentReady({ pay } = {}) {
      this.checkoutLoading = false;
      this.paymentInfoValid = true;
      this.payFunction = pay;
    },
    onPaymentChange(payment) {
      this.checkoutLoading = true;
      this.paymentInfoValid = false;
      this.payment = payment;
    },
    async paymentSuccess({ nonce } = {}) {
      this.paymentInProgress = true;
      this.nonce = nonce;

      this.$store
        .dispatch("onPaymentSuccess", {
          type: this.payment,
          campaignSlug: this.campaignSlug,
          nonce: this.nonce,
        })
        .then((response) => {
          // if flik: we need to redirct to flik for payment
          if (this.payment === "flik") {
            if (response.data.redirect_url) {
              window.location.href = response.data.redirect_url;
            } else {
              throw new Error("No redirect url in response.");
            }
            return;
          }

          // if card: braintree payment is done, redirect to thank you page
          // if upn: email was sent, redirect to thank you page
          if (this.thankYouUrl) {
            // FIXME: this thankYouUrl is fucked, its not respecting the
            // correct url from api, and is just set to a boolean in the store
            window.location.href = this.thankYouUrl;
          } else {
            const options = { name: "thankYou" };
            if (this.lang) {
              options.params = { lang: this.lang };
            }
            this.$router.push(options);
          }
        })
        .catch((error) => {
          this.paymentInProgress = false;
          // eslint-disable-next-line no-console
          console.error("Napaka pri klicu na strežnik.");
          // eslint-disable-next-line no-console
          console.error(error);
          this.error = error.response;
        });
    },
    paymentError(error) {
      this.paymentInProgress = false;
      // eslint-disable-next-line no-console
      console.error("Napaka pri plačilu.");
      // eslint-disable-next-line no-console
      console.error(error);
      this.error = error;
    },
    async continueToNextStage() {
      if (this.canContinueToNextStage) {
        if (this.payFunction) {
          this.payFunction();
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.cart-total {
  text-align: right;
  background-color: rgba(black, 0.15);
  padding: 0.5rem 1rem;
  margin: auto auto 0 auto;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  width: 100%;
  max-width: 350px;

  i {
    font-weight: 600;
    font-size: 1.25rem;
    margin-left: 0.25rem;
  }
}
</style>
