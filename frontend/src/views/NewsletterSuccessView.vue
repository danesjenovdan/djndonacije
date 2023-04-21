<template>
  <div class="checkout">
    <checkout-stage no-header show-djnd-footer>
      <template v-slot:content v-if="success == true">
        <div class="row justify-content-center">
          <div class="col-md-6 col-lg-4">
            <img class="img-fluid" src="../assets/hvala.png" />
          </div>
        </div>
        <div class="row justify-content-center">
          <h2 class="thankyou__title">Hvala!</h2>
          <p class="text-center">
            Tvoja prijava na novičnik je potrjena. Se slišimo kmalu!
          </p>
        </div>
      </template>
      <template v-slot:content v-if="failure == true">
        <div class="row justify-content-center">
          <h2 class="thankyou__title">Oh ne!</h2>
          <p class="text-center">
            Nekaj je šlo narobe, tvoja prijava ni potrjena.
          </p>
          <p class="text-center">
            Prosim, opiši nam problem na
            <a href="mailto:vsi@danesjenovdan.si">vsi@danesjenovdan.si</a>.
          </p>
        </div>
      </template>
      <div v-if="loading" class="payment-loader">
        <div class="lds-dual-ring" />
      </div>
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
      success: false,
      failure: false,
      loading: true,
    };
  },
  async mounted() {
    // store token
    const token = this.$route.query.token;
    if (token) {
      this.$store.commit("setToken", token);
    }
    // store email
    const email = this.$route.query.email;
    if (email) {
      this.$store.commit("setEmail", email);
    }

    const segment_id = this.$route.query.segment_id;

    if (!(email && token && segment_id)) {
      this.$router.push("/404");
    } else {
      this.$store
        .dispatch("confirmNewsletterSubscription", { segment_id: segment_id })
        .then((response) => {
          if (response.status === 200) {
            this.success = true;
          } else {
            // catch error
            console.log("Not successful", response);
            this.failure = true;
          }
        })
        .catch((error) => {
          // catch error
          console.log("Error", error);
          this.failure = true;
        })
        .finally(() => {
          this.loading = false;
        });
    }
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
    font-weight: 300;
    // text-transform: uppercase;
    // font-style: italic;
    margin: 16px 0;

    @include media-breakpoint-up(md) {
      font-size: 4rem;
      // font-weight: 700;
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
