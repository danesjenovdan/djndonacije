<template>
  <checkout-stage show-terms>
    <template #title>
      {{ title }}
    </template>
    <template #content>
      <div v-if="loading" class="payment-loader">
        <div class="lds-dual-ring" />
      </div>
      <div class="change-monthly">
        <h2>
          {{ $t("selectAmountView.selectAmount") }}
          <strong v-if="recurringDonation">{{
            $t("selectAmountView.monthly")
          }}</strong>
          {{ $t("selectAmountView.donation") }}
        </h2>
        <template v-if="paymentOptions.monthly">
          <!-- eslint-disable vue/no-v-html -->
          <a
            @click.prevent="setRecurringDonation(!recurringDonation)"
            v-html="
              $t('selectAmountView.donateFrequency--template', {
                frequency: $t(
                  recurringDonation
                    ? 'selectAmountView.donateOnce--word'
                    : 'selectAmountView.donateMonthly--word',
                ),
              })
            "
          />
          <!-- eslint-enable vue/no-v-html -->
        </template>
      </div>
      <div class="donation-options">
        <donation-option
          v-for="(dp, i) in filteredDonationPresets"
          :key="`presets-${i}`"
          :donation-preset="dp"
          :is-selected="dp.amount === chosenAmount"
        />
        <div
          v-for="n in 10"
          :key="`flex-spacer-${n}`"
          class="donation-option"
        />
      </div>
    </template>
    <template #footer>
      <div class="confirm-button-container">
        <confirm-button
          key="next-select-amount"
          :disabled="!canContinueToNextStage"
          :text="$t('selectAmountView.supportUs')"
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
import DonationOption from "../components/DonationOption.vue";
import ConfirmButton from "../components/ConfirmButton.vue";

export default {
  components: {
    ConfirmButton,
    DonationOption,
    CheckoutStage,
  },
  data() {
    return {
      loading: true,
    };
  },
  computed: {
    title() {
      return this.$store.getters.getTitle;
    },
    subtitle() {
      return this.$store.getters.getSubtitle;
    },
    donationPresets() {
      return this.$store.getters.getDonationPresets;
    },
    paymentOptions() {
      return this.$store.getters.getPaymentOptions;
    },
    recurringDonation() {
      return this.$store.getters.getRecurringDonation;
    },
    chosenAmount() {
      return this.$store.getters.getChosenAmount;
    },
    filteredDonationPresets() {
      return this.donationPresets.filter((dp) =>
        this.recurringDonation
          ? dp.monthly === this.recurringDonation
          : dp.oneTime !== this.recurringDonation,
      );
    },
    canContinueToNextStage() {
      return this.chosenAmount >= 1 && !this.loading;
    },
  },
  watch: {
    donationPresets(newDP) {
      this.loading = newDP.length === 0;
    },
  },
  async mounted() {
    this.loading = this.donationPresets.length === 0;

    if (this.$route.query.mesecna) {
      this.$store.commit("setRecurringDonation", true);
    }
  },
  methods: {
    setRecurringDonation(value) {
      this.$store.commit("setRecurringDonation", value);
    },
    selectDonationPreset(sdp) {
      this.$store.commit("setChosenAmount", sdp.amount);
    },
    continueToNextStage() {
      if (this.recurringDonation) {
        this.$router.push({ name: "info" });
      } else {
        this.$router.push({ name: "payment" });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.donation-options {
  display: flex;
  flex-direction: column;

  @include media-breakpoint-up(md) {
    flex-wrap: wrap;
    flex-direction: row;
    margin-left: -0.75rem;
    margin-right: -0.75rem;
  }

  .donation-option {
    @include media-breakpoint-up(md) {
      flex: 1 1 250px;
      flex-direction: column;
      align-items: stretch;
      margin-left: 0.75rem;
      margin-right: 0.75rem;
    }
  }
}

.change-monthly {
  text-align: center;
  margin-bottom: 3rem;
  margin-top: -1.5rem;

  a {
    font-size: 1rem;
    font-weight: 600;
    font-style: italic;
    color: inherit;
    text-decoration: none;
    cursor: pointer;

    @include media-breakpoint-up(md) {
      font-size: 1.5rem;
    }

    :deep(em) {
      font-style: inherit;
      text-decoration: underline;
    }

    &:hover {
      text-decoration: none;

      :deep(em) {
        text-decoration: none;
      }
    }
  }
}
</style>
