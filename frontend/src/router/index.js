import { createRouter, createWebHistory, RouterView } from "vue-router";
import SelectAmountView from "../views/SelectAmountView.vue";
import InfoView from "../views/InfoView.vue";
import PaymentView from "../views/PaymentView.vue";
import ThankYouView from "../views/ThankYouView.vue";
import ManageDonationsView from "../views/ManageDonationsView.vue";
import ManageNewsletterView from "../views/ManageNewsletterView.vue";

import i18n from "../i18n";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/:locale?",
      component: RouterView,
      children: [
        // user settings
        {
          path: "urejanje-donacij",
          name: "manageDonations",
          component: ManageDonationsView,
          meta: {
            title: "Urejanje donacij",
          },
        },
        //
        // donations
        {
          path: ":campaignSlug/doniraj",
          name: "selectAmount",
          component: SelectAmountView,
          // alias: '/:campaignSlug/doniraj/izberi'
        },
        {
          path: ":campaignSlug/doniraj/info",
          name: "info",
          component: InfoView,
        },
        {
          path: ":campaignSlug/doniraj/placilo",
          name: "payment",
          component: PaymentView,
        },
        {
          path: ":campaignSlug/doniraj/hvala",
          name: "thankYou",
          component: ThankYouView,
          meta: {
            title: "Hvala!",
          },
        },
        {
          path: ":campaignSlug/urejanje-narocnine",
          name: "manageNewsletter",
          component: ManageNewsletterView,
          meta: {
            title: "Urejanje naročnine",
          },
        },
      ],
    },
  ],
});

router.beforeEach((to, from, next) => {
  document.title = to.meta?.title ?? "Danes je nov dan";

  // use the language from the routing param or default language
  let language = to.params.locale;
  if (!language) {
    language = "sl";
  }
  i18n.global.locale = language;

  next();
})

export default router;
