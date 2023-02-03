import { createStore } from "vuex";
import axios from "axios";

// const api = "http://localhost:8000";
const api = 'https://podpri.lb.djnd.si';

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
      }
      
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
        'upn': state.campaignData.has_upn,
        'oneTime': state.campaignData.has_braintree,
        'monthly': state.campaignData.has_braintree_subscription,
      }
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
      state.campaignData.has_braintree_subscription = options.has_braintree_subscription;
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
        `${api}/api/donation-campaign/${payload.donationSlug}/`
      );

      context.commit("setDonationCampaignId", data.data.id);
      context.commit("setTitle", data.data.title);
      context.commit("setSubtitle", data.data.subtitle);
      context.commit("setDonationPresets", data.data.amounts);
      context.commit("setPaymentOptions", {
        'has_upn': data.data.has_upn,
        'has_braintree': data.data.has_braintree,
        'has_braintree_subscription': data.data.has_braintree_subscription
      });
      context.commit("setHasNewsletter", data.data.add_to_mailing);
      context.commit("setRedirectToThankYou", data.data.redirect_url);
      context.commit("setCSSFile", data.data.css_file);
      
      // if redirect url exists
      if (data.data.redirect_url) {
        context.commit("setRedirectToThankYou", true);
      }
    },
    async verifyQuestion(context, payload) {
      return await axios.get(
        `${api}/api/generic-donation/${
          payload.donationSlug
        }/?question_id=1&answer=${encodeURIComponent(
          payload.answer
        )}&email=${encodeURIComponent(payload.email)}`
      );
    },
    async onPaymentSuccess(context, payload) {
      const paymentURL = context.getters.getRecurringDonation
        ? `${api}/api/generic-donation/subscription/${payload.donationSlug}/`
        : `${api}/api/generic-donation/${payload.donationSlug}/`;

      return await axios.post(paymentURL, {
        payment_type: payload.nonce ? 'braintree' : 'upn',
        nonce: payload.nonce,
        customer_id: context.getters.getCustomerId,
        amount: context.getters.getChosenAmount,
        email: context.getters.getEmail,
        mailing: context.getters.getSubscribeToNewsletter
      });
    },
    // TODO: cancel subscription
  },
});

export default store;
