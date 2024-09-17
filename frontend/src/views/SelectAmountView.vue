<template>
  <div class="checkout">
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
  </div>
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
    const campaignSlug = this.$route.params.campaignSlug;
    const lang = this.$route.params.locale;
    
    return {
      campaignSlug,
      lang,
      loading: false,
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
    CSSFile() {
      return this.$store.getters.getCSSFile;
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
  async mounted() {
    // kliči backend API, da dobimo informacije o kampanji
    if (this.donationPresets.length === 0) {
      this.loading = true;

      this.$store.dispatch('getCampaignData', { campaignSlug: this.campaignSlug }).then(() => {
        if (this.CSSFile) {
          this.loadCSS(this.CSSFile);
        }
        this.loading = false;
      });
    }

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
    async continueToNextStage() {
      if (this.canContinueToNextStage) {
        const options = { name: "info" };
        if (this.lang) {
          options.params = { locale: this.lang }
        }
        this.$router.push(options);
      }
    },
    loadCSS(filename) {
      // if (filesAdded.indexOf(filename) !== -1) return;
      const head = document.getElementsByTagName("head")[0]; // Creating link element
      const style = document.createElement("link");
      style.href = filename;
      style.type = "text/css";
      style.rel = "stylesheet";
      head.append(style); // Adding the name of the file to keep record
      // filesAdded += ` ${filename}`;
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout {
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
}
</style>
