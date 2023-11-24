<template>
  <div class="checkout">
    <checkout-stage show-terms>
      <template v-slot:title> Podatki </template>
      <template v-slot:content>
        <div v-if="loading" class="payment-loader">
          <div class="lds-dual-ring" />
        </div>
        <div class="info-content">
          <div class="form-group">
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="E-naslov"
              class="form-control form-control-lg"
            />
          </div>
          <div class="custom-control custom-checkbox" v-if="hasNewsletter">
            <input
              id="info-newsletter"
              v-model="subscribeToNewsletter"
              type="checkbox"
              name="subscribeNewsletter"
              class="custom-control-input"
            />
            <label class="custom-control-label" for="info-newsletter"
              >Obveščajte me o novih projektih in aktivnostih.</label
            >
          </div>
          <hr />
          <p>
            Zadnje čase nas pogosto napadajo roboti. Ker se želimo prepričati,
            da si človek, prosim vpiši spodnje znake.
          </p>
          <div class="form-group">
            <div v-if="robotError" class="alert alert-danger py-2 my-2">
              Napačen odgovor.
            </div>
            <div ref="captcha"></div>
          </div>
          <div class="lonec-medu">
            <input
              type="text"
              name="name"
              placeholder="Your full name please"
              v-model="honeyPotName"
            />
          </div>
        </div>
      </template>
      <template v-slot:footer>
        <div class="confirm-button-container">
          <confirm-button
            key="next-info"
            :disabled="!canContinueToNextStage"
            :loading="infoSubmitting"
            text="Naprej"
            arrow
            hearts
            @click.native="continueToNextStage"
          />
        </div>
        <div class="secondary-link">
          <router-link :to="{ name: 'selectAmount' }">Nazaj</router-link>
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
    const campaignSlug = this.$route.params.campaignSlug;

    return {
      campaignSlug,
      answer: "",
      honeyPotName: "",
      robotError: false,
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

    if (this.$refs.captcha && !document.querySelector("#djncaptcha")) {
      const s = document.createElement("script");
      s.dataset.inputName = "captcha";
      s.dataset.locale = "sl";
      s.src = "https://captcha.lb.djnd.si/js/djncaptcha.js";
      this.$refs.captcha.appendChild(s);
    }
  },
  methods: {
    async continueToNextStage() {
      if (this.canContinueToNextStage) {
        if (this.honeyPotName !== "") {
          console.error("Preveč medu.");
        } else {
          const captchaApi = window.djnCAPTCHA["captcha"];
          if (!captchaApi) {
            this.robotError = true;
            return;
          }
          this.loading = true;
          this.$store
            .dispatch("verifyCaptcha", {
              campaignSlug: this.campaignSlug,
              captcha: captchaApi.value(),
              email: this.email,
            })
            .then((checkoutResponse) => {
              captchaApi.remove();
              this.$store.commit("setToken", checkoutResponse.data.token);
              this.$store.commit(
                "setCustomerId",
                checkoutResponse.data.customer_id
              );
              this.$router.push({ name: "payment" });
            })
            .catch((error) => {
              captchaApi.reload();
              this.loading = false;
              this.robotError = true;
            });
        }
      }
    },
    goBack() {
      this.$router.push({ name: "selectAmount" });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.lonec-medu {
  display: none !important;
}

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
