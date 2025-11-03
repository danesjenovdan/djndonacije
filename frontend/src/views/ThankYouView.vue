<template>
  <div class="checkout">
    <checkout-stage no-header>
      <template #content>
        <div class="row justify-content-center my-5">
          <img class="img-fluid" src="../assets/hvala.svg" />
        </div>
        <div class="row justify-content-center">
          <h2 class="thankyou__title">{{ $t("thankYouView.title") }}</h2>
          <p v-if="!transactionId" class="text-center">
            {{ $t("thankYouView.note") }}
          </p>
          <div v-else class="info-content">
            <p>
              {{ $t("infoView.whyEmailPost") }}
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
        </div>
      </template>
      <template v-if="transactionId" #footer>
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
    CheckoutStage,
    ConfirmButton,
  },
  data() {
    return {
      transactionId: this.$route.query.transaction_id || null,
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
    hasNewsletter() {
      return this.$store.getters.getHasNewsletter;
    },
    canContinueToNextStage() {
      return this.infoValid;
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
  },
  methods: {
    async continueToNextStage() {
      if (this.canContinueToNextStage) {
        this.infoSubmitting = true;
        this.$store
          .dispatch("afterPaymentAddEmail", {
            transaction_id: this.transactionId,
            email: this.email,
            mailing: this.subscribeToNewsletter,
          })
          .then(() => {
            this.transactionId = null;
            this.infoSubmitting = false;
          })
          .catch((error) => {
            this.infoSubmitting = false;
            // eslint-disable-next-line no-console
            console.error("Napaka pri klicu na strežnik.");
            // eslint-disable-next-line no-console
            console.error(error);
          });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout {
  .row {
    width: 100%;
    max-width: 540px;
    margin: 0 auto;
  }

  .img-fluid {
    width: 12rem;
  }

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
  }

  .back {
    color: #333333;
    font-weight: 600;
    font-size: 16px;
    font-style: italic;
    text-decoration: underline;

    &:hover {
      text-decoration: none;
    }
  }

  .thankyou__title {
    font-size: 1.85rem;
    text-align: center;
    font-weight: 600;
    text-transform: uppercase;
    font-style: italic;
    margin: 30px 0;
  }

  .info-content p {
    padding-left: 0;
    padding-right: 0;
  }
}
</style>
