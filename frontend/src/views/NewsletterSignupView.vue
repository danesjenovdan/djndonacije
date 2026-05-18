<template>
  <div class="checkout">
    <checkout-stage show-terms no-header>
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
              <div v-for="q in newsletterQuestions" class="custom-control custom-checkbox">
                <input
                  :id="`question-${q.id}`"
                  v-model="newsletterAnswers[q.id]"
                  type="checkbox"
                  :name="`question-${q.id}`"
                  class="custom-control-input"
                />
                <label class="custom-control-label" :for="`question-${q.id}`">
                  <span>
                    {{ lang === 'en' ? q.question_en : q.question_sl }}
                    <a v-if="q.url" :href="q.url">{{ lang === 'en' ? q.url_text_en : q.url_text_sl }}</a>
                  </span>
                </label>
              </div>
              <div class="captcha-container">
                <div v-if="robotError" class="alert alert-danger py-2 my-2">
                  {{ $t("infoView.wrongAnswer") }}
                </div>
                <div ref="captcha"></div>
              </div>
              <p class="bots-text">
                {{ $t("infoView.bots") }}
              </p>
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
      robotError: false,
      infoSubmitting: false,
      signupDone: false,
      newsletterAnswers: {},
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
    questions() {
      return this.$store.getters.getQuestions;
    },
    newsletterQuestions() {
      return this.questions.filter((q) => q.field_type === "segment_checkbox");
    },
    lang() {
      return this.$store.getters.getLang;
    },
    canSubmit() {
      return this.infoValid;
    },
    infoValid() {
      const trueAnswers = this.newsletterQuestions.filter((q) => this.newsletterAnswers[q.id]);
      if (!trueAnswers.length) {
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
    }
    if (segmentId) {
      this.segmentId = segmentId;
    }

    if (this.$refs.captcha && !document.querySelector("#vajbcha")) {
      const s = document.createElement("script");
      s.dataset.inputName = "captcha";
      s.dataset.locale = this.lang;
      s.src = "https://vajbcha.danesjenovdan.si/js/vajbcha.js";
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
        // set answers for newsletter questions
        this.newsletterQuestions.forEach((q) => {
          this.$store.commit(
            "setAnswer",
            { questionId: q.id, answer: this.newsletterAnswers[q.id] || false }
          );
        });

        // submit
        this.infoSubmitting = true;
        this.robotError = false;
        const captchaApi = window.vajbcha.captcha;
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

  .bots-text {
    max-width: 360px;
    margin: 0 auto;
    padding-top: 1rem;
    font-size: 1rem;
    font-weight: 300;
  }

  .captcha-container {
    :deep(#vajbcha) {
      iframe {
        margin-inline: auto;
      }
    }
  }
}
</style>
