<template>
  <div class="card-payment">
    <payment-error v-if="error" />
    <template v-else-if="!braintreeInitialized">
      <form>
        <div class="captcha-container">
          <div v-if="robotError" class="alert alert-danger py-2 my-2">
            {{ $t("infoView.wrongAnswer") }}
          </div>
          <div ref="captcha"></div>
          <div class="form-group">
            <label>{{ $t("infoView.bots") }}</label>
          </div>
        </div>
      </form>
    </template>
    <template v-else>
      <form>
        <div class="form-group">
          <div class="lonec-medu">
            <input
              v-model="honeyPotName"
              type="text"
              name="name"
              placeholder="Your full name please"
            />
            <input
              v-model="honeyPotAddress"
              type="text"
              name="address"
              placeholder="Your address please"
            />
            <input
              v-model="honeyPotPost"
              type="text"
              name="post"
              placeholder="Your postal code and office name please"
            />
          </div>
          <div
            id="cc-number"
            :class="[
              'form-control',
              'form-control-lg',
              { focus: numberFocused },
            ]"
          />
        </div>
        <div class="form-group">
          <div
            id="cc-expirationDate"
            :class="[
              'form-control',
              'form-control-lg',
              { focus: expirationDateFocused },
            ]"
          />
        </div>
        <div class="form-group">
          <div
            id="cc-cvv"
            :class="['form-control', 'form-control-lg', { focus: cvvFocused }]"
          />
        </div>
      </form>
      <div class="card-info">
        {{ $t("payment.cardNote") }}
        <br />
        <img
          src="https://s3.amazonaws.com/braintree-badges/braintree-badge-light.png"
          width="164"
          height="44"
          border="0"
        />
      </div>
    </template>
  </div>
</template>

<script>
import braintree from "braintree-web";
import PaymentError from "./Error.vue";

export default {
  name: "CardPayment",
  components: {
    PaymentError,
  },
  props: {
    token: {
      type: String,
      required: true,
    },
    amount: {
      type: Number,
      required: true,
    },
    recurring: {
      type: Boolean,
      default: false,
    },
    email: {
      type: String,
      default: "",
    },
    campaignSlug: {
      type: String,
      required: true,
    },
  },
  emits: [
    "captcha-ready",
    "captcha-done",
    "ready",
    "success",
    "error",
    "payment-start",
    "validity-change",
  ],
  data() {
    return {
      robotError: false,
      braintreeInitialized: false,
      hostedFieldsInstance: null,
      threeDSecureInstance: null,
      error: null,
      numberFocused: false,
      expirationDateFocused: false,
      cvvFocused: false,
      formValid: false,
      paymentInProgress: false,
      honeyPotName: "",
      honeyPotAddress: "",
      honeyPotPost: "",
    };
  },
  watch: {
    token(newVal) {
      if (newVal) {
        this.initBraintree();
      }
    },
  },
  mounted() {
    if (this.token) {
      this.initBraintree();
      return;
    }

    if (this.$refs.captcha && !document.querySelector("#djncaptcha")) {
      const s = document.createElement("script");
      s.dataset.inputName = "captcha";
      s.dataset.locale = this.lang;
      s.src = "https://captcha.lb.djnd.si/js/djncaptcha.js";
      this.$refs.captcha.appendChild(s);
      if (this.recurring) {
        this.$emit("captcha-ready", { submit: this.submitCaptchaRecurring });
      } else {
        this.$emit("captcha-ready", { submit: this.submitCaptcha });
      }
    }
  },
  methods: {
    submitCaptcha() {
      const captchaApi = window.djnCAPTCHA.captcha;
      if (!captchaApi) {
        this.robotError = true;
        return;
      }
      this.$emit("captcha-done");
      this.$store
        .dispatch("verifyCaptcha", {
          captcha: captchaApi.value(),
        })
        .then((checkoutResponse) => {
          captchaApi.remove();
          this.$store.commit("setToken", checkoutResponse.data.token);
          this.$store.commit(
            "setCustomerId",
            checkoutResponse.data.customer_id,
          );
        })
        .catch(() => {
          captchaApi.reload();
          this.$emit("captcha-ready", { submit: this.submitCaptcha });
          this.robotError = true;
        });
    },
    submitCaptchaRecurring() {
      const captchaApi = window.djnCAPTCHA.captcha;
      if (!captchaApi) {
        this.robotError = true;
        return;
      }
      this.$emit("captcha-done");
      this.$store
        .dispatch("verifyCaptchaRecurring", {
          captcha: captchaApi.value(),
          email: this.email,
          campaignSlug: this.campaignSlug,
        })
        .then((checkoutResponse) => {
          captchaApi.remove();
          this.$store.commit("setToken", checkoutResponse.data.token);
          this.$store.commit(
            "setCustomerId",
            checkoutResponse.data.customer_id,
          );
        })
        .catch(() => {
          captchaApi.reload();
          this.$emit("captcha-ready", { submit: this.submitCaptchaRecurring });
          this.robotError = true;
        });
    },
    async initBraintree() {
      if (!this.braintreeInitialized && braintree) {
        this.braintreeInitialized = true;
        try {
          const clientInstance = await braintree.client.create({
            authorization: this.token,
          });
          const placeholderStyle = {
            // 'font-style': 'italic',
            // 'font-weight': '300',
            color: "#444",
            // 'text-decoration': 'underline',
          };
          const options = {
            client: clientInstance,
            styles: {
              input: {
                "font-size": "19.2px",
                "font-family": "monospace",
              },
              "input.invalid": {
                color: "#dd786b",
              },
              // placeholder styles need to be individually adjusted
              "::-webkit-input-placeholder": placeholderStyle,
              "::-ms-input-placeholder": placeholderStyle,
              "::placeholder": placeholderStyle,
            },
            fields: {
              number: {
                selector: "#cc-number",
                placeholder: this.$t("paymentView.cardNumber"),
              },
              expirationDate: {
                selector: "#cc-expirationDate",
                placeholder: this.$t("paymentView.expiryDate"),
              },
              cvv: {
                selector: "#cc-cvv",
                placeholder: "CVV",
              },
            },
          };
          this.hostedFieldsInstance =
            await braintree.hostedFields.create(options);
          this.threeDSecureInstance = await braintree.threeDSecure.create({
            client: clientInstance,
            version: 2,
          });

          this.hostedFieldsInstance.on("focus", (event) => {
            this[`${event.emittedBy}Focused`] = true;
          });
          this.hostedFieldsInstance.on("blur", (event) => {
            this[`${event.emittedBy}Focused`] = false;
          });
          this.hostedFieldsInstance.on("validityChange", (event) => {
            const formValid = Object.keys(event.fields).every((key) => {
              return event.fields[key].isValid;
            });
            this.formValid = formValid;
            this.$emit("validity-change", formValid);
          });
          this.hostedFieldsInstance.on("inputSubmitRequest", () => {
            this.payWithCreditCard();
          });

          this.$emit("ready", { pay: this.payWithCreditCard });
        } catch (error) {
          // eslint-disable-next-line no-console
          // console.error(error);
          this.error = error;
          this.$emit("error", { error });
        }
      }
    },
    payWithCreditCard() {
      if (
        this.honeyPotName !== "" ||
        this.honeyPotAddress !== "" ||
        this.honeyPotPost !== ""
      ) {
        this.error = "Preveč medu.";
        this.$emit("error", "Preveč medu.");
      } else if (this.hostedFieldsInstance && !this.paymentInProgress) {
        this.paymentInProgress = true;
        this.$emit("payment-start");
        this.error = null;
        this.hostedFieldsInstance
          .tokenize({
            vault: true,
          })
          .then((payload) => {
            return this.threeDSecureInstance.verifyCard({
              onLookupComplete: (data, next) => next(),
              amount: this.amount,
              nonce: payload.nonce,
              bin: payload.details.bin,
              challengeRequested: true,
            });
          })
          .then((payload) => {
            if (!payload.liabilityShifted) {
              // eslint-disable-next-line no-console
              console.log("Liability did not shift", payload);
              this.error = "Avtentikacija plačila ni uspela.";
              this.$emit("error", { message: this.error });
            } else {
              this.$emit("success", { nonce: payload.nonce });
            }
          })
          .catch((error) => {
            // eslint-disable-next-line no-console
            // console.error(error);
            this.error = error.message;
            this.$emit("error", { error });
          });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.card-payment {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 360px;
  margin: 0 auto;

  .captcha-container {
    :deep(#djncaptcha) {
      iframe {
        margin-inline: auto;
      }
    }

    label {
      font-size: 1rem;
      font-weight: 300;
      text-align: center;
      display: block;
      padding-top: 1rem;
    }
  }

  .focus {
    border: 1px solid black;
    box-shadow: 0 0 0 0.2rem rgba(black, 0.25);
  }

  .loader-container {
    display: flex;
    justify-content: center;
    margin: 3rem 0;

    &.load-container--small {
      margin: 1rem 0;
    }
  }

  .card-info {
    font-weight: 300;
    font-size: 1rem;
    text-align: center;

    img {
      margin-top: 0.5rem;
    }
  }
}
</style>
