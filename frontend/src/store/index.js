import { createStore } from "vuex";
import axios from "axios";

// const api = "http://localhost:8000";
const api = "https://podpri.lb.djnd.si";

const store = createStore({
  state() {
    return {
      campaignData: {
        donationCampaignId: "",
        title: "",
        subtitle: "",
        donationPresets: [],
        has_upn: false,
        has_braintree: false,
        has_braintree_subscription: false,
        CSSFile: "",
        redirectToThankYou: "",
        hasNewsletter: false,
      },
      userData: {
        chosenAmount: 0,
        recurringDonation: false,
        email: "",
        subscribeToNewsletter: false,
        token: "",
        customerId: "",
      },
    };
  },
  getters: {
    getDonationCampaignId(state) {
      return state.campaignData.donationCampaignId;
    },
    getTitle(state) {
      return state.campaignData.title;
    },
    getSubtitle(state) {
      return state.campaignData.subtitle;
    },
    getDonationPresets(state) {
      return state.campaignData.donationPresets;
    },
    getPaymentOptions(state) {
      return {
        upn: state.campaignData.has_upn,
        oneTime: state.campaignData.has_braintree,
        monthly: state.campaignData.has_braintree_subscription,
      };
    },
    getCSSFile(state) {
      return state.campaignData.CSSFile;
    },
    getRedirectToThankYou(state) {
      return state.campaignData.redirectToThankYou;
    },
    getHasNewsletter(state) {
      return state.campaignData.hasNewsletter;
    },
    getChosenAmount(state) {
      return state.userData.chosenAmount;
    },
    getRecurringDonation(state) {
      return state.userData.recurringDonation;
    },
    getEmail(state) {
      return state.userData.email;
    },
    getSubscribeToNewsletter(state) {
      return state.userData.subscribeToNewsletter;
    },
    getToken(state) {
      return state.userData.token;
    },
    getCustomerId(state) {
      return state.userData.customerId;
    },
  },
  mutations: {
    setDonationCampaignId(state, id) {
      state.campaignData.donationCampaignId = id;
    },
    setTitle(state, title) {
      state.campaignData.title = title;
    },
    setSubtitle(state, subtitle) {
      state.campaignData.subtitle = subtitle;
    },
    setDonationPresets(state, newDonationPresets) {
      // create the custom preset object
      const customPreset = {
        custom: true,
        amount: null,
        description: "Vnesi poljuben znesek!",
        selected: false,
        eventName: "custom",
        monthly: true,
        oneTime: true,
      };

      // create objects from the api
      const donationPresets = [];
      for (let dp of newDonationPresets) {
        donationPresets.push({
          custom: false,
          amount: dp.amount,
          description: "",
          selected: false,
          eventName: "",
          monthly: dp.recurring_amount,
          oneTime: dp.one_time_amount,
        });
      }

      // add the custom one
      donationPresets.push(customPreset);

      state.campaignData.donationPresets = donationPresets;
    },
    setPaymentOptions(state, options) {
      state.campaignData.has_upn = options.has_upn;
      state.campaignData.has_braintree = options.has_braintree;
      state.campaignData.has_braintree_subscription =
        options.has_braintree_subscription;
    },
    setCSSFile(state, file) {
      state.campaignData.CSSFile = file;
    },
    setRedirectToThankYou(state, redirect) {
      state.campaignData.redirectToThankYou = redirect;
    },
    setHasNewsletter(state, add_to_mailing) {
      state.campaignData.hasNewsletter = !!add_to_mailing;
    },
    setChosenAmount(state, amount) {
      state.userData.chosenAmount = amount;
    },
    setRecurringDonation(state, recurringDonation) {
      state.userData.recurringDonation = recurringDonation;
    },
    setEmail(state, email) {
      state.userData.email = email;
    },
    setSubscribeToNewsletter(state, subscribeToNewsletter) {
      state.userData.subscribeToNewsletter = subscribeToNewsletter;
    },
    setToken(state, token) {
      state.userData.token = token;
    },
    setCustomerId(state, customerId) {
      state.userData.customerId = customerId;
    },
  },
  actions: {
    async getCampaignData(context, payload) {
      const data = await axios.get(
        `${api}/api/donation-campaign/${payload.campaignSlug}/`
      );

      context.commit("setDonationCampaignId", data.data.id);
      context.commit("setTitle", data.data.title);
      context.commit("setSubtitle", data.data.subtitle);
      context.commit("setDonationPresets", data.data.amounts);
      context.commit("setPaymentOptions", {
        has_upn: data.data.has_upn,
        has_braintree: data.data.has_braintree,
        has_braintree_subscription: data.data.has_braintree_subscription,
      });
      context.commit("setHasNewsletter", data.data.add_to_mailing);
      context.commit("setRedirectToThankYou", data.data.redirect_url);
      context.commit("setCSSFile", data.data.css_file);

      // if redirect url exists
      if (data.data.redirect_url) {
        context.commit("setRedirectToThankYou", true);
      }
    },
    async getUserDonations(context, payload) {
      const url = `${api}/api/subscriptions/my?token=${context.getters.getToken}&email=${context.getters.getEmail}`;
      return await axios.get(url);
    },
    // TODO: spremeni to v get en sam subscription za newsletter (glede na campaign slug)
    async getUserNewsletterSubscriptions(context, payload) {
      const url = `${api}/api/segments/my?token=${context.getters.getToken}&email=${context.getters.getEmail}`;
      return await axios.get(url);
    },
    async verifyQuestion(context, payload) {
      return await axios.get(
        `${api}/api/generic-donation/${
          payload.campaignSlug
        }/?question_id=2&answer=${encodeURIComponent(
          payload.answer
        )}&email=${encodeURIComponent(payload.email)}`
      );
    },
    async onPaymentSuccess(context, payload) {
      const paymentURL = context.getters.getRecurringDonation
        ? `${api}/api/generic-donation/subscription/${payload.campaignSlug}/`
        : `${api}/api/generic-donation/${payload.campaignSlug}/`;

      return await axios.post(paymentURL, {
        payment_type: payload.nonce ? "braintree" : "upn",
        nonce: payload.nonce,
        customer_id: context.getters.getCustomerId,
        amount: context.getters.getChosenAmount,
        email: context.getters.getEmail,
        mailing: context.getters.getSubscribeToNewsletter,
      });
    },
    async cancelDonationSubscription(context, payload) {
      const url = `${api}/api/generic-donation/cancel-subscription/`;

      try {
        const response = await axios.post(url, {
          token: encodeURIComponent(context.getters.getToken),
          subscription_id: encodeURIComponent(payload.subscription_id),
        });
        return response;
      } catch (err) {
        console.log("ERROR at sending request", err.message);
        return null;
      }
    },
    async cancelNewsletterSubscription(context, payload) {
      const url = `${api}/api/segments/${payload.segment_id}/contact/?token=${context.getters.getToken}&email=${context.getters.getEmail}`;

      try {
        const response = await axios.delete(url);
        return response;
      } catch (err) {
        console.log("ERROR at sending request", err.message);
        return null;
      }
    },
  },
});

export default store;
