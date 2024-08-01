<template>
  <div class="checkout">
    <div v-if="success && !last_cancelled_newsletter" class="alert alert-success text-center">
      <p v-if="lang == 'eng'" class="my-3">
        You have successfully unsubscribed and we have deleted your data.
      </p>
      <p v-else class="my-3">
        Odjavili smo te od vseh novičnikov in izbrisali tvoje podatke.
      </p>
    </div>
    <div v-if="success && last_cancelled_newsletter" class="alert alert-success text-center">
      <p v-if="lang == 'eng'" class="my-3">
        You have successfully unsubscribed.
      </p>
      <p v-else class="my-3">
        Odjava je uspešna!
      </p>
    </div>
    <div v-if="error && lang != 'eng'" class="alert alert-danger text-center">
      <p class="my-3">
        Zgodila se je napaka.
      </p>
      <p v-if="errorMessage == 'No such subscriber'" class="my-3">
        <b>Uporabnik_ca s temi podatki ne obstaja.</b>
      </p>
      <p class="my-3">
        Piši nam na
        <a href="mailto:vsi@danesjenovdan.si">vsi@danesjenovdan.si</a> in bomo
        takoj razrešili težavo.
      </p>
    </div>
    <div v-if="error && lang == 'eng'" class="alert alert-danger text-center">
      <p class="my-3">
        An error occurred.
        <br />Contact us at
        <a href="mailto:info@disco.si">info@disco.si</a>, and we will solve the problem as soon as possible.
      </p>
    </div>
    <checkout-stage no-header :show-djnd-footer="!lang" :show-disco-footer="lang == 'eng'">
      <template v-slot:content>
        <div class="row justify-content-center my-4" v-for="segment in this.campaignSubscriptions" :key="segment.id">
          <div class="col-md-8">
            <div class="row">
              <div class="col-md-6">
                <p class="m-0" v-if="segment.id === 21">
                  Odjavi me od Občasnika.
                </p>
                <p class="small-paragraph" v-if="segment.id === 21">
                  Z izbiro te možnosti te bomo odjavili od našega Občasnika. Če
                  prejemaš kakšen drug novičnik, za katerega skrbimo na Danes je
                  nov dan, pa ga lahko še naprej pričakuješ v nabiralniku.
                </p>
                <p class="m-0" v-else-if="lang == 'eng'">
                  Unsubscribe me from the <strong>DISCO Slovenia</strong> newsletter.
                </p>
                <p class="m-0" v-else>
                  Odjavi me od novičnika <strong>{{ segment.name }}</strong>.
                </p>
              </div>
              <div class="col-md-6">
                <more-button :disabled="loading" :text="lang == 'eng' ? 'Yes, unsubscribe me.' : 'Da, odjavi me.'"
                  class="my-2" color="secondary" @click="cancelSubscription(segment.name, segment.id)" />
              </div>
            </div>
            <div class="row mt-4">
              <div class="col-12">
                <hr />
              </div>
            </div>
          </div>
        </div>
        <div class="row justify-content-center mb-4">
          <div class="col-md-4">
            <p class="m-0" v-if="lang == 'eng'">
              Unsubscribe me from <strong>all newsletters</strong> sent out by Danes je nov dan (Today is a new day) and
              <strong>delete my data</strong>.
            </p>
            <p class="m-0" v-else>
              Odjavi me od <strong>vseh novičnikov</strong>, za katere skrbi
              Danes je nov dan, in <strong>izbriši moje podatke</strong>.
            </p>
            <p class="small-paragraph mb-0">Novičniki, na katere si prijavljen_a:</p>
            <ul>
              <li v-for="segment in this.allSubscriptions" class="my-0">{{ segment.name }}</li>
            </ul>
            <p class="small-paragraph" v-if="lang == 'eng'">
              By selecting this option, all your data will be deleted from our database, and you will no longer receive
              any communication from us. We will keep your email address only if you are registered for the DISCO
              Slovenia
              conference, or if you donate to Today is a New Day or any of the associated organizations for which we
              collect contributions.
            </p>
            <p class="small-paragraph" v-else>
              Z izbiro te možnosti bomo iz naše baze izbrisali vse tvoje
              podatke, od nas pa v prihodnje ne boš prejemal_a nobenega
              sporočila več. Tvoj e-naslov bomo hranili le v primeru, da doniraš
              Danes je nov dan ali eni od organizacij, za katere zbiramo
              donacije.
            </p>
          </div>
          <div class="col-md-4">
            <more-button :disabled="loading"
              :text="lang == 'eng' ? 'Yes, delete my data.' : 'Da, izbriši moje podatke.'" class="my-2"
              color="secondary" @click="deleteUserData()" />
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
  props: ["lang"],
  components: {
    CheckoutStage,
    MoreButton,
  },
  data() {
    const campaignSlug = this.$route.params.campaignSlug;

    return {
      campaignSubscriptions: [],
      allSubscriptions: [],
      loading: true,
      campaignSlug,
      email: null,
      token: null,
      success: false,
      error: false,
      errorMessage: "",
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

    // get campaign subscriptions list
    this.$store
      .dispatch("getUserNewsletterSubscriptions", {
        campaign: this.campaignSlug,
      })
      .then((response) => {
        if (response.status === 200) {
          this.campaignSubscriptions = response.data.segments;
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
        this.errorMessage = error?.response?.data?.detail
      })
      .finally(() => {
        this.loading = false;
      });

    // get all subscriptions list
    this.$store
      .dispatch("getUserNewsletterSubscriptions", {})
      .then((response) => {
        if (response.status === 200) {
          this.allSubscriptions = response.data.segments;
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
        this.errorMessage = error?.response?.data?.detail
      })
      .finally(() => {
        this.loading = false;
      });
  },
  methods: {
    async cancelSubscription(campaign_name, segment_id) {
      this.loading = true;

      this.$store
        .dispatch("cancelNewsletterSubscription", {
          segment_id: segment_id,
        })
        .then((response) => {
          if (response.status === 200) {
            this.campaignSubscriptions = this.campaignSubscriptions.filter(
              (campaign) => campaign.id != segment_id
            );
            this.allSubscriptions = this.allSubscriptions.filter(
              (campaign) => campaign.id != segment_id
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
          this.errorMessage = error?.response?.data?.detail
        })
        .finally(() => {
          this.loading = false;
        });
    },
    async deleteUserData() {
      this.loading = true;

      this.$store
        .dispatch("deleteUserData")
        .then((response) => {
          if (response.status === 204) {
            this.subscriptions = [];
            this.success = true;
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
          this.errorMessage = error?.response?.data?.detail
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout-stage {
  p, li {
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

  p.small-paragraph, li {
    font-size: 16px;
  }
}</style>
