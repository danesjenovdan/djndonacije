<template>
  <div class="checkout">
    <div v-if="success" class="alert alert-success text-center">
      <p class="my-3">
        Naročnina na novičnik {{ last_cancelled_newsletter }} je uspešno
        prekinjena.
      </p>
    </div>
    <div v-if="error" class="alert alert-danger text-center">
      <p class="my-3">
        Zgodila se je napaka.
        <br />Piši nam na
        <a href="mailto:vsi@danesjenovdan.si">vsi@danesjenovdan.si</a> in bomo
        takoj razrešili težavo.
      </p>
    </div>
    <checkout-stage no-header show-djnd-footer>
      <template v-slot:content>
        <div
          class="row justify-content-center my-4"
          v-for="segment in this.subscriptions"
          :key="segment.id"
        >
          <div class="col-md-4">
            <p class="m-0">
              Odjavi me od <strong>{{ segment.name }}</strong> novičnika
            </p>
          </div>
          <div class="col-md-4">
            <more-button
              :disabled="loading"
              :text="'Da, potrjujem odjavo.'"
              class="my-2"
              color="secondary"
              @click="cancelSubscription(segment.name, segment.id)"
            />
          </div>
        </div>
        <div class="row justify-content-center my-4">
          <div class="col-md-4">
            <p class="m-0">
              Odjavi me od <strong>vseh novičnikov</strong>, za katere skrbi
              Danes je nov dan, in <strong>izbriši moje podatke</strong>.
            </p>
          </div>
          <div class="col-md-4">
            <more-button
              :disabled="loading"
              :text="'Da, izbriši moje podatke.'"
              class="my-2"
              color="secondary"
              @click="deleteUserData()"
            />
          </div>
        </div>
        <div v-if="loading" class="payment-loader">
          <div class="lds-dual-ring" />
        </div>
      </template>
    </checkout-stage>
  </div>
</template>

<script>
import CheckoutStage from "../components/CheckoutStage.vue";
import MoreButton from "../components/MoreButton.vue";

export default {
  components: {
    CheckoutStage,
    MoreButton,
  },
  data() {
    const campaignSlug = this.$route.params.campaignSlug;

    return {
      subscriptions: [],
      loading: true,
      campaignSlug,
      email: null,
      token: null,
      success: false,
      error: false,
      last_cancelled_newsletter: null,
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

    if (!(email && token)) {
      this.$router.push("/404");
    }

    // get subscriptions list
    this.$store
      .dispatch("getUserNewsletterSubscriptions")
      .then((response) => {
        if (response.status === 200) {
          this.subscriptions = response.data.segments;
        } else {
          // catch error
          console.log("Not successful", response);
          this.success = false;
          this.error = true;
        }
      })
      .catch((error) => {
        // catch error
        console.log("Error", error);
        this.success = false;
        this.error = true;
      })
      .finally(() => {
        this.loading = false;
      });
  },
  methods: {
    async cancelSubscription(campaign_name, segment_id) {
      this.loading = true;

      // popravi, da ne bo več seznam, ko bo obstajal primeren endpoint
      this.$store
        .dispatch("cancelNewsletterSubscription", {
          segment_id: segment_id,
        })
        .then((response) => {
          if (response.status === 200) {
            this.subscriptions = this.subscriptions.filter(
              (campaign) => campaign.segment_id != segment_id
            );
            this.success = true;
            this.last_cancelled_newsletter = campaign_name;
          } else {
            // catch error
            console.log("Not successful", response);
            this.success = false;
            this.error = true;
          }
        })
        .catch((error) => {
          // catch error
          this.success = false;
          this.error = true;
          console.log("Error", error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    // TODO: dopolni, ko bo obstajal ta endpoint
    async deleteUserData() {},
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout-stage {
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
}
</style>
