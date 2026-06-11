<template>
  <checkout-stage no-header>
    <template #content>
      <div class="row justify-content-center my-5">
        <img class="img-fluid" src="../assets/hvala.svg" />
      </div>
      <div class="row justify-content-center">
        <h2 class="thankyou__title">{{ $t("thankYouView.title") }}</h2>
        <p v-if="!transactionId && !wasUpn" class="text-center thankyou__note">
          <template v-if="campaignSlug === 'danes-je-nov-dan'">
            {{ $t("thankYouView.note") }}
          </template>
          <template v-else>
            {{ $t("thankYouView.note-generic") }}
          </template>
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
                <a v-if="q.url" :href="q.url" target="_blank">{{ lang === 'en' ? q.url_text_en : q.url_text_sl }}</a>
              </span>
            </label>
          </div>
        </div>
      </div>
    </template>
    <template v-if="transactionId || wasUpn" #footer>
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
      campaignSlug: this.$route.params.campaignSlug,
      transactionId: this.$route.query.transaction_id || null,
      wasUpn: this.$route.query.upn === "true",
      infoSubmitting: false,
      newsletterAnswers: {},
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
    questions() {
      return this.$store.getters.getQuestions;
    },
    newsletterQuestions() {
      return this.questions.filter((q) => q.field_type === "segment_checkbox");
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
        // set answers for newsletter questions
        this.newsletterQuestions.forEach((q) => {
          this.$store.commit(
            "setAnswer",
            { questionId: q.id, answer: this.newsletterAnswers[q.id] || false }
          );
        });

        // submit
        this.infoSubmitting = true;
        this.$store
          .dispatch("afterPaymentAddEmail", {
            campaignSlug: this.campaignSlug,
            transactionId: this.transactionId,
            email: this.email,
          })
          .then(() => {
            this.transactionId = null;
            this.wasUpn = false;
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

  .thankyou__note {
    color: inherit;
  }

  .info-content p {
    padding-left: 0;
    padding-right: 0;
    color: inherit;
  }
}
</style>
