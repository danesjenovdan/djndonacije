<template>
  <div class="checkout">
    <checkout-stage no-header>
      <template #content>
        <div class="row justify-content-center my-5">
          <div class="image-container">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
              <path
                d="M64.1 83.3c-7.82 0-14.92 3.4-18.1 8.7a2 2 0 103.43 2c2.47-4.09 8.23-6.73 14.67-6.73 6.07 0 11.69 2.44 14.32 6.21a2 2 0 103.28-2.28c-3.4-4.86-10.15-7.9-17.6-7.9zM48.59 70.41a2 2 0 002.82-2.82L44.83 61l6.58-6.59a2 2 0 00-2.82-2.82L42 58.17l-6.59-6.58a2 2 0 00-2.82 2.82L39.17 61l-6.58 6.59a2 2 0 102.82 2.82L42 63.83zm46.82-18.82a2 2 0 00-2.82 0L86 58.17l-6.59-6.58a2 2 0 00-2.82 2.82L83.17 61l-6.58 6.59a2 2 0 102.82 2.82L86 63.83l6.59 6.58a2 2 0 002.82-2.82L88.83 61l6.58-6.59a2 2 0 000-2.82z"
              />
              <path
                d="M120 24H53a2.73 2.73 0 01-3-3v-6a6.7 6.7 0 00-7-7H7a6.7 6.7 0 00-7 7v97.25a8.31 8.31 0 002.4 5.8 6.44 6.44 0 004.11 1.89A2 2 0 007 120h114c4.32 0 7-4.15 7-8V32c0-5.08-2.92-8-8-8zm4 88c0 1.93-1.21 4-3 4H7.43a2.49 2.49 0 00-.43 0 2.37 2.37 0 01-1.76-.75 4.3 4.3 0 01-1.21-3V15a2.73 2.73 0 013-3H43a2.73 2.73 0 013 3v6a6.7 6.7 0 007 7h67c2.88 0 4 1.12 4 4z"
              />
            </svg>
          </div>
        </div>
        <div class="row justify-content-center">
          <h2 class="paymenterror__title">
            {{ $t("paymentErrorView.title") }}
          </h2>
          <!-- eslint-disable vue/no-v-html -->
          <p
            class="text-center"
            v-html="$t('paymentErrorView.note', { startHref })"
          />
          <!-- eslint-enable vue/no-v-html -->
        </div>
      </template>
    </checkout-stage>
  </div>
</template>

<script>
import CheckoutStage from "../components/CheckoutStage.vue";

export default {
  components: {
    CheckoutStage,
  },
  data() {
    return {
      startHref: ".",
    };
  },
  mounted() {
    if (typeof window !== "undefined") {
      const hrefPart = window.location.href.split("/napaka")[0];
      this.startHref = hrefPart;
    }
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout {
  .image-container {
    max-width: 190px;
    margin: 0 auto;

    @include media-breakpoint-up(md) {
      max-width: 280px;
    }
  }

  p {
    font-size: 1.25rem;
    color: #333333;
    font-weight: 200;
    width: 100%;
    margin-top: 20px;
    margin-bottom: 20px;
    padding-left: 30px;
    padding-right: 30px;

    @include media-breakpoint-up(md) {
      font-size: 1.5rem;
      padding: 0;
    }
  }

  .paymenterror__title {
    font-size: 1.5rem;
    text-align: center;
    font-weight: 600;
    text-transform: uppercase;
    font-style: italic;
    margin: 30px 0;

    @include media-breakpoint-up(md) {
      font-size: 3.5rem;
      font-weight: 600;
    }
  }
}
</style>
