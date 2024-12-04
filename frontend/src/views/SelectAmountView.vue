<template>
  <checkout-stage show-terms>
    <template v-slot:title>
      {{ title }}
    </template>
    <template v-slot:content>
      <div v-if="loading" class="payment-loader">
        <div class="lds-dual-ring" />
      </div>
      <div class="change-monthly">
        <h2>{{ $t('selectAmountView.selectAmount') }} <strong v-if="recurringDonation">{{
            $t('selectAmountView.monthly')
            }}</strong> {{
          $t('selectAmountView.donation') }}</h2>
        <a v-if="recurringDonation && paymentOptions.monthly" @click.prevent="setRecurringDonation(false)">
          {{ $t('selectAmountView.donateOnce') }}
        </a>
        <a v-if="!recurringDonation && paymentOptions.monthly" @click.prevent="setRecurringDonation(true)">
          {{ $t('selectAmountView.donateMonthly') }}
        </a>
      </div>
      <div class="donation-options">
        <donation-option v-for="(dp, i) in filteredDonationPresets" :key="`presets-${i}`" :donation-preset="dp"
          :is-selected="dp.amount === this.chosenAmount" />
        <div v-for="n in 10" :key="`flex-spacer-${n}`" class="donation-option" />
      </div>
    </template>
    <template v-slot:footer>
      <div class="confirm-button-container">
        <confirm-button key="next-select-amount" :disabled="!canContinueToNextStage"
          :text="$t('selectAmountView.supportUs')" arrow hearts @click.native="continueToNextStage" />
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
          : dp.oneTime !== this.recurringDonation
      );
    },
    canContinueToNextStage() {
      return this.chosenAmount >= 1 && !this.loading;
    },
  },
  watch: {
    donationPresets(newDP, oldDP) {
      this.loading = newDP.length === 0;
    }
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
      this.$router.push({ name: "info", query: { flik_enabled: this.$route.query.flik_enabled }, });
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
    text-decoration: underline;
    cursor: pointer;

    @include media-breakpoint-up(md) {
      font-size: 1.5rem;
    }

    &:hover {
      text-decoration: none;
    }
  }
}
</style>
