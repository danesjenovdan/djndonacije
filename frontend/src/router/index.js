import { createRouter, createWebHistory, RouterView } from "vue-router";
import DonateView from "../views/DonateView.vue";
import SelectAmountView from "../views/SelectAmountView.vue";
import InfoView from "../views/InfoView.vue";
import PaymentView from "../views/PaymentView.vue";
import ThankYouView from "../views/ThankYouView.vue";
import PaymentErrorView from "../views/PaymentErrorView.vue";
import ManageDonationsView from "../views/ManageDonationsView.vue";
import ManageNewsletterView from "../views/ManageNewsletterView.vue";
import RootView from "../views/RootView.vue";

import i18n from "../i18n";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // root
    {
      path: "/",
      name: "root",
      component: RootView,
    },
    // user settings
    {
      path: "/urejanje-donacij",
      name: "manageDonations",
      component: ManageDonationsView,
      meta: {
        title: "Urejanje donacij",
      },
    },
    //
    // donations
    {
      path: "/:campaignSlug/doniraj",
      component: DonateView,
      name: "donate",
      children: [
        {
          path: "",
          name: "selectAmount",
          component: SelectAmountView,
        },
        {
          path: "info",
          name: "info",
          component: InfoView,
        },
        {
          path: "placilo",
          name: "payment",
          component: PaymentView,
        },
      ],
    },
    {
      path: "/:campaignSlug/doniraj/hvala",
      name: "thankYou",
      component: ThankYouView,
      meta: {
        title: "Hvala!",
      },
    },
    {
      path: "/:campaignSlug/doniraj/napaka",
      name: "paymentError",
      component: PaymentErrorView,
      meta: {
        title: "Napaka!",
      },
    },
    {
      path: "/:campaignSlug/urejanje-narocnine",
      name: "manageNewsletter",
      component: ManageNewsletterView,
      meta: {
        title: "Urejanje naročnine",
      },
    },
  ],
});

router.beforeEach((to, from, next) => {
  document.title = to.meta?.title ?? "Danes je nov dan";

  // use the language from the routing param or default language
  // let language = to.params.locale;
  // if (!language) {
  //   language = "sl";
  // }
  // i18n.global.locale = language;

  next();
})

export default router;
