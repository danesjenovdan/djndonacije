<template>
  <div class="checkout">
    <div v-if="error" class="alert alert-danger">
      <p>
        Zgodila se je napaka. Naš strežnik je ni mogel rešiti, prejel je
        naslednje sporočilo:
        <strong>{{
          error.error && error.error.message ? error.error.message : error.data
        }}</strong>
      </p>
      <p>
        Zaračunali ti nismo ničesar, ves denar je še vedno na tvoji kartici.
        Predlagamo, da osvežiš stran in poskusiš ponovno. Če ne bo šlo, nam piši
        na
        <a href="mailto:vsi@danesjenovdan.si">vsi@danesjenovdan.si</a> in ti
        bomo poskusili pomagati.
      </p>
    </div>
    <checkout-stage stage="payment">
      <template v-slot:title> Plačilo </template>
      <template v-slot:content>
        <div class="payment-container">
          <payment-switcher
            v-if="paymentOptions.upn && paymentOptions.oneTime"
            :recurring="recurringDonation"
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
          <div class="cart-total">
            <span>Znesek za plačilo</span>
            <i>{{ chosenAmount }} €</i>
          </div>
        </div>
      </template>
      <template v-slot:footer>
        <div class="confirm-button-container">
          <confirm-button
            key="next-payment"
            :disabled="!canContinueToNextStage"
            :loading="paymentInProgress"
            text="DONIRAJ"
            arrow
            hearts
            @click.native="continueToNextStage"
          />
        </div>
        <div class="secondary-link">
          <router-link :to="{ name: 'info' }">Nazaj</router-link>
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
import PaymentSwitcher from "../components/Payment/Switcher.vue";

export default {
  components: {
    ConfirmButton,
    CheckoutStage,
    CardPayment,
    UpnPayment,
    PaymentSwitcher,
  },
  data() {
    const donationSlug = this.$route.params.donationSlug;
    const payment = this.$store.getters.getPaymentOptions.oneTime ? 'card' : 'upn'

    return {
      donationSlug,
      error: null,
      payment: payment,
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
          donationSlug: this.donationSlug,
          nonce: this.nonce,
        })
        .then((response) => {
          // redirect to thank you page
          if (this.thankYouUrl) {
            window.location.href = this.thankYouUrl;
          } else {
            this.$router.push({ name: "thankYou" });
          }
        })
        .catch((error) => {
          this.paymentInProgress = false;
          // eslint-disable-next-line no-console
          console.error("Napaka pri klicu na strežnik.");
          console.error(error);
          this.error = error.response;
        });
    },
    paymentError(error) {
      this.paymentInProgress = false;
      // eslint-disable-next-line
      console.error("Napaka pri plačilu.");
      // eslint-disable-next-line
      console.error(error);
      this.error = error;
    },
    async continueToNextStage() {
      if (this.canContinueToNextStage) {
        if (this.payFunction) {
          this.payFunction();
        }
      }
      return;
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
