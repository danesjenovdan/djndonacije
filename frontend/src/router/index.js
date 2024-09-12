import { createRouter, createWebHistory } from "vue-router";
import SelectAmountView from "../views/SelectAmountView.vue";
import InfoView from "../views/InfoView.vue";
import PaymentView from "../views/PaymentView.vue";
import ThankYouView from "../views/ThankYouView.vue";
import ManageDonationsView from "../views/ManageDonationsView.vue";
import ManageNewsletterView from "../views/ManageNewsletterView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // user settings
    {
      path: "/urejanje-donacij",
      name: "manageDonations",
      component: ManageDonationsView,
      meta: {
        title: 'Urejanje donacij',
      },
    },
    //
    // donations
    {
      path: "/:campaignSlug/doniraj",
      name: "selectAmount",
      component: SelectAmountView,
      // alias: '/:campaignSlug/doniraj/izberi'
    },
    {
      path: "/:campaignSlug/doniraj/info",
      name: "info",
      component: InfoView,
    },
    {
      path: "/:campaignSlug/doniraj/placilo",
      name: "payment",
      component: PaymentView,
    },
    {
      path: "/:campaignSlug/doniraj/hvala",
      name: "thankYou",
      component: ThankYouView,
      meta: {
        title: 'Hvala!',
      },
    },
    {
      path: "/:campaignSlug/urejanje-narocnine",
      name: "manageNewsletter",
      component: ManageNewsletterView,
      meta: {
        title: 'Urejanje naročnine',
      },
    },
    {
      path: "/:campaignSlug/manage-subscription",
      name: "manageNewsletterEng",
      component: ManageNewsletterView,
      props: { lang: "eng" },
      meta: {
        title: 'Manage my subscription',
      },
    },
    //
  ],
});

router.beforeEach((to, from) => {
  document.title = to.meta?.title ?? 'Doniraj za nov dan!'
})

export default router;
