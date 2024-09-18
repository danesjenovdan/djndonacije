<template>
    <div class="checkout">
        <RouterView />
    </div>
</template>

<script>

export default {
    data() {
        const campaignSlug = this.$route.params.campaignSlug;

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
        this.$store.dispatch('getCampaignData', { campaignSlug: this.campaignSlug }).then(() => {
            if (this.CSSFile) {
                this.loadCSS(this.CSSFile);
            }
        });
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
    },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";
</style>
