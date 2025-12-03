<template>
  <div class="checkout">
    <checkout-stage no-header>
      <template #content>
        <template v-if="!signupDone">
          <div class="row justify-content-center">
            <h2 class="signup__title">{{ $t("newsletterSignup.title") }}</h2>
            <div class="info-content">
              <div class="form-group">
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  :placeholder="$t('infoView.email')"
                  class="form-control form-control-lg"
                />
              </div>
              <div class="custom-control custom-checkbox">
                <input
                  id="info-newsletter"
                  v-model="consentCheckbox"
                  type="checkbox"
                  name="subscribeNewsletter"
                  class="custom-control-input"
                />
                <label class="custom-control-label" for="info-newsletter">{{
                  $t("infoView.newsletterLabel")
                }}</label>
              </div>
              <p>
                {{ $t("infoView.bots") }}
              </p>
              <div class="captcha-container">
                <div v-if="robotError" class="alert alert-danger py-2 my-2">
                  {{ $t("infoView.wrongAnswer") }}
                </div>
                <div ref="captcha"></div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="row justify-content-center my-5">
            <h2 class="signup__title">{{ $t("newsletterSignup.thankYou") }}</h2>
            <img class="img-fluid" src="../assets/hvala.svg" />
            <div class="info-content">
              <p>{{ $t("newsletterSignup.thankYouConfirm") }}</p>
            </div>
          </div>
        </template>
      </template>
      <template v-if="!signupDone" #footer>
        <div class="confirm-button-container">
          <confirm-button
            key="next-info"
            :disabled="!canSubmit"
            :loading="infoSubmitting"
            :text="$t('newsletterSignup.signMeUp')"
            arrow
            hearts
            @click="onSubmit"
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
    const { campaignSlug } = this.$route.params;

    return {
      campaignSlug,
      segmentId: null,
      consentCheckbox: false,
      robotError: false,
      infoSubmitting: false,
      signupDone: false,
    };
  },
  computed: {
    CSSFile() {
      return this.$store.getters.getCSSFile;
    },
    email: {
      get() {
        return this.$store.getters.getEmail;
      },
      set(value) {
        this.$store.commit("setEmail", value);
      },
    },
    canSubmit() {
      return this.infoValid;
    },
    infoValid() {
      if (!this.consentCheckbox) {
        return false;
      }
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
    // kliči backend API, da dobimo informacije o kampanji
    this.$store
      .dispatch("getCampaignData", { campaignSlug: this.campaignSlug })
      .then(() => {
        if (this.CSSFile) {
          this.loadCSS(this.CSSFile);
        }
      });

    const { email, segment_id: segmentId } = this.$route.query;
    if (email) {
      this.email = email;
      this.consentCheckbox = true;
    }
    if (segmentId) {
      this.segmentId = segmentId;
    }

    if (this.$refs.captcha && !document.querySelector("#djncaptcha")) {
      const s = document.createElement("script");
      s.dataset.inputName = "captcha";
      s.dataset.locale = this.lang;
      s.src = "https://captcha.lb.djnd.si/js/djncaptcha.js";
      this.$refs.captcha.appendChild(s);
    }
  },
  methods: {
    loadCSS(filename) {
      const head = document.getElementsByTagName("head")[0];
      const style = document.createElement("link");
      style.href = filename;
      style.type = "text/css";
      style.rel = "stylesheet";
      head.append(style);
    },
    async onSubmit() {
      if (this.canSubmit) {
        this.infoSubmitting = true;
        this.robotError = false;
        const captchaApi = window.djnCAPTCHA.captcha;
        if (!captchaApi) {
          this.infoSubmitting = false;
          this.robotError = true;
          return;
        }
        this.$store
          .dispatch("newsletterSafeSubscribe", {
            email: this.email,
            segmentId: this.segmentId,
            captcha: captchaApi.value(),
          })
          .then((response) => {
            // eslint-disable-next-line no-console
            console.log("Newsletter signup response:", response);
            captchaApi.remove();
            this.infoSubmitting = false;
            this.robotError = false;
            this.signupDone = true;
          })
          .catch((error) => {
            // eslint-disable-next-line no-console
            console.error("Newsletter signup error:", error);
            captchaApi.reload();
            this.infoSubmitting = false;
            this.robotError = true;
            this.signupDone = false;
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
    font-size: 21px;
    color: #333333;
    font-weight: 200;
    width: 100%;
    max-width: 872px;
    margin-top: 20px;
    margin-bottom: 20px;
    padding-left: 30px;
    padding-right: 30px;
  }

  .signup__title {
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
    text-align: center;
  }

  .captcha-container {
    :deep(#djncaptcha) {
      iframe {
        margin-inline: auto;
      }
    }
  }
}
</style>
