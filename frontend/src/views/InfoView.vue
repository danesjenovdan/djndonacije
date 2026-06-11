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
          <div
            v-for="q in newsletterQuestions"
            class="custom-control custom-checkbox"
          >
            <input
              :id="`question-${q.id}`"
              v-model="newsletterAnswers[q.id]"
              type="checkbox"
              :name="`question-${q.id}`"
              class="custom-control-input"
            />
            <label class="custom-control-label" :for="`question-${q.id}`">
              <template v-if="lang === 'en'">
                <span
                  v-if="q.question_en?.startsWith('html:')"
                  v-html="q.question_en.slice(5)"
                ></span>
                <span v-else>
                  {{ q.question_en }}
                  <a v-if="q.url" :href="q.url" target="_blank">{{
                    q.url_text_en
                  }}</a>
                </span>
              </template>
              <template v-else>
                <span
                  v-if="q.question_sl?.startsWith('html:')"
                  v-html="q.question_sl.slice(5)"
                ></span>
                <span v-else>
                  {{ q.question_sl }}
                  <a v-if="q.url" :href="q.url" target="_blank">{{
                    q.url_text_sl
                  }}</a>
                </span>
              </template>
            </label>
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
    chosenAmount() {
      return this.$store.getters.getChosenAmount;
    },
    recurringDonation() {
      return this.$store.getters.getRecurringDonation;
    },
    questions() {
      return this.$store.getters.getQuestions;
    },
    newsletterQuestions() {
      return this.questions.filter((q) => q.field_type === "segment_checkbox");
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
        // set answers for newsletter questions
        this.newsletterQuestions.forEach((q) => {
          this.$store.commit("setAnswer", {
            questionId: q.id,
            answer: this.newsletterAnswers[q.id] || false,
          });
        });

        // continue to next stage
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
