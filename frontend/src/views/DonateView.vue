<template>
  <div class="checkout">
    <RouterView v-if="$store.getters.getDonationCampaignId" />
  </div>
</template>

<script>
export default {
  data() {
    const { campaignSlug } = this.$route.params;

    return {
      campaignSlug,
    };
  },
  computed: {
    CSSFile() {
      return this.$store.getters.getCSSFile;
    },
  },
  async mounted() {
    // kliči backend API, da dobimo informacije o kampanji
    this.$store
      .dispatch("getCampaignData", { campaignSlug: this.campaignSlug })
      .then(() => {
        if (this.CSSFile) {
          this.loadCSS(this.CSSFile);
        }
      });

    this.getReferrer();
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
    getReferrer() {
      let referrers = [];
      if (typeof document !== "undefined") {
        referrers.push(`document.referrer: ${document.referrer}`);
      }
      if (typeof window !== "undefined") {
        referrers.push(`window.top === window: ${window.top === window}`);
        const origins = Array.from(window.location.ancestorOrigins);
        referrers.push(
          `window.location.ancestorOrigins: ${origins.join(", ")}`,
        );
        const searchParams = new URLSearchParams(window.location.search);
        referrers.push(`URL Parameters:`);
        for (const [key, value] of searchParams.entries()) {
          const keyLower = key.toLowerCase();
          if (
            keyLower.includes("referrer") ||
            keyLower.includes("referer") ||
            keyLower.startsWith("utm_")
          ) {
            referrers.push(`  - ${key}: ${value}`);
          }
        }
      }
      const referrerInfo = referrers.join("\n");
      console.log("Referrer information:", referrerInfo);
      if (referrerInfo) {
        this.$store.commit("setReferrerInfo", referrerInfo);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";
</style>
