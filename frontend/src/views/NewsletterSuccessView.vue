<template>
  <div class="checkout">
    <checkout-stage no-header show-djnd-footer>
      <template v-slot:content>
        <div class="row justify-content-center my-5">
          <div class="col-md-6 col-lg-4">
            <img class="img-fluid" src="../assets/hvala.svg" />
          </div>
        </div>
        <div class="row justify-content-center">
          <h2 class="thankyou__title">Hvala za prijavo na novičnik!</h2>
          <p class="text-center">
            Z zanimivimi temami in novicmai te bomo zalagali vsak mesec, pisali
            pa ti bomo tudi, kadar naredimo kaj dobrega in kadar se dogaja kaj
            pomembnega.
          </p>
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
    return {};
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout {
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

    @include media-breakpoint-up(md) {
      font-size: 30px;
      padding: 0;
    }
  }

  .back {
    color: #333333;
    font-weight: 600;
    font-size: 20px;
    font-style: italic;
    text-decoration: underline;

    @include media-breakpoint-down(sm) {
      font-size: 16px;
    }

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

    @include media-breakpoint-up(md) {
      font-size: 5rem;
      font-weight: 700;
    }

    .icon {
      display: none;

      @include media-breakpoint-up(md) {
        display: inline-block;
        width: 5rem;
        height: 5rem;
        margin: -0.75rem 0;
      }
    }
  }
}
</style>
